
from typing import List, Dict

DOC_TYPES = [
    "Special Conditions", "Memorandum of Sale", "Lease", "Office Copy Entry",
    "Title Plan", "Replies to Enquiries", "Searches", "EPC", "Addendum",
]

KEYWORDS = {
    "Special Conditions": ["special conditions", "buyer to pay", "administration fee"],
    "Lease": ["lease", "ground rent", "service charge", "term of years"],
    "Office Copy Entry": ["title number", "proprietorship register"],
    "Title Plan": ["title plan", "ordnance survey"],
    "Replies to Enquiries": ["enquiries", "cpse"],
    "Searches": ["local authority search", "drainage", "environmental"],
    "EPC": ["energy performance"],
    "Addendum": ["addendum", "updated"],
}

def classify_documents(pages: List[Dict]) -> List[Dict]:
    docs = []
    for p in pages:
        text = (p.get("text") or "").lower()
        dtype = "Other"
        for dt, kws in KEYWORDS.items():
            if any(kw in text for kw in kws):
                dtype = dt
                break
        docs.append({"type": dtype, "page": p["page"], "text": p["text"]})
    return docs
