
import io
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

    reader = PdfReader(io.BytesIO(content))
    for i, _ in enumerate(reader.pages):
        # First try native text
        text = ""
        try:
            text = extract_text(io.BytesIO(content), page_numbers=[i]) or ""
        except Exception:
            text = ""

        # Fallback to Textract if configured and empty
        if not text and settings.USE_TEXTRACT and _textract is not None:
            resp = _textract.detect_document_text(Document={"Bytes": content})
            text = "\n".join(b["Text"] for b in resp.get("Blocks", []) if b.get("BlockType") == "LINE")

        pages.append({"page": i+1, "text": text})
    return pages
