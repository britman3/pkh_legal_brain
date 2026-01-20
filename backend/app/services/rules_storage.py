import json
import uuid
from pathlib import Path
from typing import List, Optional
from app.models.rules import Rule, RuleCreate, RuleUpdate

RULES_FILE = Path(__file__).parent.parent.parent / "data" / "rules.json"


def _ensure_data_dir():
    RULES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not RULES_FILE.exists():
        RULES_FILE.write_text("[]")


def _load_rules() -> List[dict]:
    _ensure_data_dir()
    return json.loads(RULES_FILE.read_text())


def _save_rules(rules: List[dict]):
    _ensure_data_dir()
    RULES_FILE.write_text(json.dumps(rules, indent=2))


def get_all_rules() -> List[Rule]:
    data = _load_rules()
    return [Rule(**r) for r in data]


def get_enabled_rules() -> List[Rule]:
    return [r for r in get_all_rules() if r.enabled]


def get_rule_by_id(rule_id: str) -> Optional[Rule]:
    for r in _load_rules():
        if r.get("id") == rule_id:
            return Rule(**r)
    return None


def create_rule(rule: RuleCreate) -> Rule:
    rules = _load_rules()
    new_rule = Rule(
        id=str(uuid.uuid4()),
        rule_type=rule.rule_type,
        value=rule.value,
        severity=rule.severity,
        instruction=rule.instruction,
        enabled=rule.enabled,
    )
    rules.append(new_rule.model_dump())
    _save_rules(rules)
    return new_rule


def update_rule(rule_id: str, updates: RuleUpdate) -> Optional[Rule]:
    rules = _load_rules()
    for i, r in enumerate(rules):
        if r.get("id") == rule_id:
            update_data = updates.model_dump(exclude_unset=True)
            rules[i] = {**r, **update_data}
            _save_rules(rules)
            return Rule(**rules[i])
    return None


def delete_rule(rule_id: str) -> bool:
    rules = _load_rules()
    original_len = len(rules)
    rules = [r for r in rules if r.get("id") != rule_id]
    if len(rules) < original_len:
        _save_rules(rules)
        return True
    return False
