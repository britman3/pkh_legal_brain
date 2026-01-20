
from textwrap import dedent
from typing import List
from app.models.rules import Rule, RuleType

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


def _build_custom_rules_section(rules: List[Rule]) -> str:
    """Build a prompt section from custom rules."""
    if not rules:
        return ""

    sections = []

    # Excluded words/phrases
    excluded = [r for r in rules if r.rule_type == RuleType.EXCLUDE_WORD]
    if excluded:
        words = ", ".join(f'"{r.value}"' for r in excluded)
        sections.append(f"EXCLUDED TERMS (never use these words/phrases in your output): {words}")

    # Severity overrides
    overrides = [r for r in rules if r.rule_type == RuleType.SEVERITY_OVERRIDE]
    if overrides:
        override_lines = []
        for r in overrides:
            line = f'- "{r.value}": classify as {r.severity.upper() if r.severity else "AMBER"}'
            if r.instruction:
                line += f" ({r.instruction})"
            override_lines.append(line)
        sections.append("SEVERITY OVERRIDES:\n" + "\n".join(override_lines))

    # Custom instructions
    custom = [r for r in rules if r.rule_type == RuleType.CUSTOM_INSTRUCTION]
    if custom:
        instructions = "\n".join(f"- {r.value}" + (f": {r.instruction}" if r.instruction else "") for r in custom)
        sections.append("ADDITIONAL INSTRUCTIONS:\n" + instructions)

    if not sections:
        return ""

    return "\n\n# User Custom Rules\n" + "\n\n".join(sections)


def build_prompt(context: dict, custom_rules: List[Rule] = None) -> dict:
    custom_rules_section = _build_custom_rules_section(custom_rules or [])

    head = "\n\n".join([
        "# PKH Checklist\n" + context["kb"]["checklist"],
        "# Glossary\n" + context["kb"]["glossary"],
        "# Gotchas\n" + context["kb"]["gotchas"],
        "# Extracted Chunks (sample)\n" + "\n\n".join(
            f"[#{i:03d} {c['meta']['doc_type']} p.{c['meta']['page']}]\n{c['content']}"
            for i, c in enumerate(context["chunks"][:50])
        )
    ])

    system_prompt = NICK_SYSTEM + custom_rules_section

    return {"system": system_prompt, "user": head}
