
from typing import List, Dict

PKH_CHECKLIST = """
RED FLAGS:
- Doubling ground rent; ground rent > £250 outside London (>£1000 in London)
- Lease term < 80 years (marriage value triggers)
- Overage/uplift clauses
- Buyer pays seller costs / auction admin fees unusual
- Missing rights of access / services easements
- Section 20 major works liabilities
- Chancel repair liability
- Flood zone 3 or subsidence notices
- Uninsurable risks / restrictive covenants
"""

GLOSSARY = """
- Office Copy Entry: Land Registry title extract.
- Title Plan: The mapped extent of the title boundaries.
- Special Conditions: Auction-specific terms that override standard ones.
"""

GOTCHAS = """
Patterns seen in past deals: hidden buyer premiums; short completion (10 business days);
service charge balancing charges; indemnity policies required; missing FENSA/GasSafe certificates.
"""

def enrich_with_rag(chunks: List[Dict]) -> Dict:
    return {
        "chunks": chunks,
        "kb": {
            "checklist": PKH_CHECKLIST,
            "glossary": GLOSSARY,
            "gotchas": GOTCHAS,
        }
    }
