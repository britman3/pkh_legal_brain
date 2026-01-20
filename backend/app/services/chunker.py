
from typing import List, Dict

MAX_CHARS = 2000

def chunk_documents(docs: List[Dict]) -> List[Dict]:
    chunks: List[Dict] = []
    for d in docs:
        t = d["text"] or ""
        if not t:
            # still create a placeholder chunk to keep page anchors
            chunks.append({"content": "", "meta": {"doc_type": d["type"], "page": d["page"]}})
            continue
        for i in range(0, len(t), MAX_CHARS):
            segment = t[i:i+MAX_CHARS]
            chunks.append({
                "content": segment,
                "meta": {"doc_type": d["type"], "page": d["page"]}
            })
    return chunks
