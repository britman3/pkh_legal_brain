from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from app.services.ocr import ocr_extract
from app.services.classify import classify_documents
from app.services.chunker import chunk_documents
from app.services.rag import enrich_with_rag
from app.services.model_router import analyze_with_router
from app.services.prompts import build_prompt
from app.services.redact import redact_sensitive
from app.services.pdf_generator import markdown_to_pdf
from app.utils.citations import attach_citations
from app.utils.address_extractor import extract_property_address
from app.utils.cost_calculator import calculate_costs
from app.database import get_db
from app.models.analysis import Analysis

router = APIRouter()

class AnalysisResponse(BaseModel):
    report_markdown: str
    flags: list[dict]
    confidence: float
    analysis_id: int


@router.post("/pack", response_model=AnalysisResponse)
async def analyze_pack(file: UploadFile = File(...), db: Session = Depends(get_db)):
    allowed_types = {
        "application/pdf",
        "application/zip",
        "application/x-zip-compressed",
        "application/x-zip",
        "application/octet-stream",
    }
    filename_lower = file.filename.lower() if file.filename else ""
    is_valid = (
        file.content_type in allowed_types or
        filename_lower.endswith('.pdf') or
        filename_lower.endswith('.zip')
    )

    if not is_valid:
        raise HTTPException(status_code=400, detail="Upload a PDF or ZIP of PDFs.")

    try:
        content = await file.read()
        file_size = len(content)
        await file.seek(0)

        pages = await ocr_extract(file)
        if not pages:
            raise HTTPException(status_code=422, detail="Could not read any pages from the file.")

        docs = classify_documents(pages)
        chunks = chunk_documents(docs)

        if not chunks:
            raise HTTPException(status_code=422, detail="No readable text extracted. Try enabling OCR.")

        safe_chunks = [redact_sensitive(c) for c in chunks]
        context = enrich_with_rag(safe_chunks)

        prompt = build_prompt(context)

        llm_result, usage_stats = await analyze_with_router(prompt, meta={
            "page_map": [c["meta"] for c in chunks],
            "size": len(pages)
        })

        report_md, flags, confidence = attach_citations(llm_result, chunks)
        property_address = extract_property_address(report_md)

        if property_address:
            print(f"✅ Extracted address: {property_address}")

        # Calculate costs
        costs = calculate_costs(usage_stats)
        print(f"💰 Anthropic cost: ${costs['anthropic_cost']:.4f}")
        print(f"💰 OpenAI cost: ${costs['openai_cost']:.4f}")
        print(f"💰 Total cost: ${costs['total_cost']:.4f}")

        analysis_record = Analysis(
            filename=file.filename or "unknown",
            file_size_bytes=file_size,
            property_address=property_address,
            anthropic_input_tokens=usage_stats.get("anthropic_input_tokens", 0),
            anthropic_output_tokens=usage_stats.get("anthropic_output_tokens", 0),
            openai_input_tokens=usage_stats.get("openai_input_tokens", 0),
            openai_output_tokens=usage_stats.get("openai_output_tokens", 0),
            anthropic_cost_usd=costs['anthropic_cost'],
            openai_cost_usd=costs['openai_cost'],
            total_cost_usd=costs['total_cost'],
            summary_text=report_md[:10000]
        )

        db.add(analysis_record)
        db.commit()
        db.refresh(analysis_record)

        print(f"💾 Saved analysis #{analysis_record.id} - Cost: ${analysis_record.total_cost_usd}")

        return AnalysisResponse(
            report_markdown=report_md,
            flags=flags,
            confidence=confidence,
            analysis_id=analysis_record.id
        )
    
    finally:
        # Ensure file is always closed
        await file.close()
        print("🔒 File handle closed")


@router.get("/download-pdf/{analysis_id}")
async def download_pdf(analysis_id: int, db: Session = Depends(get_db)):
    """
    Download the analysis report as a PDF.
    """
    # Fetch the analysis from database
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Generate PDF from the stored markdown
    pdf_buffer = markdown_to_pdf(
        report_markdown=analysis.summary_text,
        property_address=analysis.property_address
    )

    # Create filename
    if analysis.property_address:
        # Clean address for filename
        clean_address = "".join(c for c in analysis.property_address if c.isalnum() or c in (' ', '-', '_'))
        clean_address = clean_address.replace(' ', '_')[:50]
        filename = f"PKH_Legal_Brain_{clean_address}.pdf"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"PKH_Legal_Brain_{timestamp}.pdf"

    # Return as downloadable file
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/list")
async def list_analyses(db: Session = Depends(get_db), limit: int = 50):
    """
    Get list of all analyses for the admin dashboard
    """
    analyses = db.query(Analysis).order_by(Analysis.created_at.desc()).limit(limit).all()

    results = []
    for a in analyses:
        results.append({
            "id": a.id,
            "filename": a.filename,
            "property_address": a.property_address,
            "file_size_mb": round(a.file_size_bytes / 1024 / 1024, 2),
            "total_cost_usd": round(a.total_cost_usd, 4),
            "created_at": a.created_at.isoformat() if a.created_at else None
        })

    return {"analyses": results, "total": len(results)}
