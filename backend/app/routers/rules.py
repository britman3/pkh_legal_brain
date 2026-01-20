from fastapi import APIRouter, HTTPException
from typing import List
from app.models.rules import Rule, RuleCreate, RuleUpdate, RuleType, Severity
from app.services import rules_storage

router = APIRouter()


@router.get("/", response_model=List[Rule])
def list_rules():
    """Get all custom rules."""
    return rules_storage.get_all_rules()


@router.get("/types")
def get_rule_types():
    """Get available rule types and severities for the UI."""
    return {
        "rule_types": [
            {"value": RuleType.EXCLUDE_WORD, "label": "Exclude Word/Phrase",
             "description": "Never mention this word or phrase in the output"},
            {"value": RuleType.SEVERITY_OVERRIDE, "label": "Severity Override",
             "description": "Change the severity level for a specific topic"},
            {"value": RuleType.CUSTOM_INSTRUCTION, "label": "Custom Instruction",
             "description": "Add a custom instruction for the AI to follow"},
        ],
        "severities": [
            {"value": Severity.RED, "label": "Red (Deal-breaker)"},
            {"value": Severity.AMBER, "label": "Amber (Caution)"},
            {"value": Severity.GREEN, "label": "Green (Standard)"},
            {"value": Severity.IGNORE, "label": "Ignore (Don't report)"},
        ]
    }


@router.post("/", response_model=Rule)
def create_rule(rule: RuleCreate):
    """Create a new custom rule."""
    return rules_storage.create_rule(rule)


@router.get("/{rule_id}", response_model=Rule)
def get_rule(rule_id: str):
    """Get a specific rule by ID."""
    rule = rules_storage.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.patch("/{rule_id}", response_model=Rule)
def update_rule(rule_id: str, updates: RuleUpdate):
    """Update an existing rule."""
    rule = rules_storage.update_rule(rule_id, updates)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.delete("/{rule_id}")
def delete_rule(rule_id: str):
    """Delete a rule."""
    if not rules_storage.delete_rule(rule_id):
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"status": "deleted"}


@router.post("/{rule_id}/toggle", response_model=Rule)
def toggle_rule(rule_id: str):
    """Toggle a rule's enabled status."""
    rule = rules_storage.get_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rules_storage.update_rule(rule_id, RuleUpdate(enabled=not rule.enabled))
