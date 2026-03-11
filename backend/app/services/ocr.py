import io
import zipfile
from typing import List, Dict
from pypdf import PdfReader
from pdfminer.high_level import extract_text
from app.config import settings

# Optional: AWS Textract client if scans are poor
try:
    import boto3
    _textract = boto3.client("textract")
except Exception:
    _textract = None

async def ocr_extract(upload_file) -> List[Dict]:
    content = await upload_file.read()
    pages: List[Dict] = []
    
    # Check if it's a ZIP file
    filename_lower = upload_file.filename.lower() if upload_file.filename else ""
    is_zip = filename_lower.endswith('.zip') or zipfile.is_zipfile(io.BytesIO(content))
    
    if is_zip:
        # Handle ZIP file - extract all PDFs inside
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            for file_info in zf.namelist():
                if file_info.lower().endswith('.pdf'):
                    pdf_content = zf.read(file_info)
                    pdf_pages = _extract_pdf_pages(pdf_content, filename=file_info)
                    pages.extend(pdf_pages)
    else:
        # Handle single PDF
        pages = _extract_pdf_pages(content, filename=upload_file.filename)
    
    return pages

def _extract_pdf_pages(pdf_content: bytes, filename: str = "") -> List[Dict]:
    """Extract text from a single PDF."""
    pages: List[Dict] = []
    
    try:
        reader = PdfReader(io.BytesIO(pdf_content))
        for i, _ in enumerate(reader.pages):
            # First try native text
            text = ""
            try:
                text = extract_text(io.BytesIO(pdf_content), page_numbers=[i]) or ""
            except Exception:
                text = ""
            
            # Fallback to Textract if configured and empty
            if not text and settings.USE_TEXTRACT and _textract is not None:
                resp = _textract.detect_document_text(Document={"Bytes": pdf_content})
                text = "\n".join(b["Text"] for b in resp.get("Blocks", []) if b.get("BlockType") == "LINE")
            
            pages.append({
                "page": i + 1,
                "text": text,
                "source": filename  # Track which PDF this came from
            })
    except Exception as e:
        print(f"Error extracting PDF {filename}: {e}")
    
    return pages
