
import re

def redact_sensitive(chunk: dict) -> dict:
    c = chunk.copy()
    text = c.get("content") or ""
    # Simple PII scrubs
    text = re.sub(r"\b[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D]\b", "[REDACTED_NI]", text, flags=re.I)
    text = re.sub(r"\b\d{8}\b", "[REDACTED_ACCT]", text)
    text = re.sub(r"[\w\.-]+@[\w\.-]+", "[REDACTED_EMAIL]", text)
    text = re.sub(r"\b\+?\d{7,}\b", "[REDACTED_PHONE]", text)
    c["content"] = text
    return c
