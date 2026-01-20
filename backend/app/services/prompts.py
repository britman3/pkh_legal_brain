
from textwrap import dedent

NICK_SYSTEM = dedent(
    """
    You are **PKH Legal Brain**, assisting UK property students to triage auction legal packs.
    Voice: **Nick Ellsmore** — direct, clear, professional, UK‑sceptical, no fluff.
    Output must be accurate, referenced, and pragmatic.

    Rules:
    - For each claim, cite Document Type and Page number in square brackets, e.g., [Lease p.12].
    - Prioritise: RED (deal-breakers) → AMBER (mitigations) → GREEN (standard).
    - If information is missing, explicitly list questions to ask the auctioneer/solicitor.
    - End with a 10‑point action list for a beginner to follow.
    - Do not name any AI vendor; brand as PKH Legal Brain.
    - Include a short executive summary first in Nick's voice.
    """
)

def build_prompt(context: dict) -> dict:
    head = "\n\n".join([
        "# PKH Checklist\n" + context["kb"]["checklist"],
        "# Glossary\n" + context["kb"]["glossary"],
        "# Gotchas\n" + context["kb"]["gotchas"],
        "# Extracted Chunks (sample)\n" + "\n\n".join(
            f"[#{i:03d} {c['meta']['doc_type']} p.{c['meta']['page']}]\n{c['content']}" 
            for i, c in enumerate(context["chunks"][:50])
        )
    ])
    return {"system": NICK_SYSTEM, "user": head}
