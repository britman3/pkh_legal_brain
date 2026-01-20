
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from app.services.ocr import ocr_extract
from app.services.classify import classify_documents
from app.services.chunker import chunk_documents
from app.services.rag import enrich_with_rag
from app.services.model_router import analyze_with_router
from app.services.prompts import build_prompt
from app.services.redact import redact_sensitive
from app.services.rules_storage import get_enabled_rules
from app.utils.citations import attach_citations

router = APIRouter()

class AnalysisResponse(BaseModel):
    report_markdown: str
    flags: list[dict]
    confidence: float

@router.post("/pack", response_model=AnalysisResponse)
async def analyze_pack(file: UploadFile = File(...)):
    if file.content_type not in {"application/pdf", "application/zip"}:
        raise HTTPException(status_code=400, detail="Upload a PDF or ZIP of PDFs.")

    # 1) Extract text & pages
    pages = await ocr_extract(file)

    if not pages:
        raise HTTPException(status_code=422, detail="Could not read any pages from the file.")

    # 2) Classify into doc types (lease, special conditions, title, plan, etc.)
    docs = classify_documents(pages)

    # 3) Chunk with anchors for citations
    chunks = chunk_documents(docs)

    if not chunks:
        raise HTTPException(status_code=422, detail="No readable text extracted. Try enabling OCR.")

    # 4) Redact sensitive fields before external calls
    safe_chunks = [redact_sensitive(c) for c in chunks]

    # 5) RAG enrichment (PKH checklist + glossary + gotchas)
    context = enrich_with_rag(safe_chunks)

    # 6) Get custom rules from dashboard
    custom_rules = get_enabled_rules()

    # 7) Build Nick-voice, RAG-augmented prompt with custom rules
    prompt = build_prompt(context, custom_rules=custom_rules)

    # 8) Route to best model(s)
    llm_result = await analyze_with_router(prompt, meta={
        "page_map": [c["meta"] for c in chunks],
        "size": len(pages)
    })

    # 9) Attach page-level citations to claims
    report_md, flags, confidence = attach_citations(llm_result, chunks)

    return AnalysisResponse(report_markdown=report_md, flags=flags, confidence=confidence)
