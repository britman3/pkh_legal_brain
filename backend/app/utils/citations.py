
from typing import Tuple, List, Dict

def attach_citations(model_text: str, chunks: List[Dict]) -> Tuple[str, list, float]:
    flags = []
    if "RED" in (model_text or ""):
        flags.append({"level": "RED"})
    confidence = 0.75
    return model_text, flags, confidence
