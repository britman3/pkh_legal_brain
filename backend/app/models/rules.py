from pydantic import BaseModel
from typing import Optional
from enum import Enum


class RuleType(str, Enum):
    EXCLUDE_WORD = "exclude_word"        # Don't mention this word/phrase
    SEVERITY_OVERRIDE = "severity_override"  # Change severity for a topic
    CUSTOM_INSTRUCTION = "custom_instruction"  # Free-form instruction


class Severity(str, Enum):
    RED = "red"
    AMBER = "amber"
    GREEN = "green"
    IGNORE = "ignore"


class Rule(BaseModel):
    id: Optional[str] = None
    rule_type: RuleType
    value: str  # The word, phrase, or topic
    severity: Optional[Severity] = None  # For severity overrides
    instruction: Optional[str] = None  # Additional context/instruction
    enabled: bool = True


class RuleCreate(BaseModel):
    rule_type: RuleType
    value: str
    severity: Optional[Severity] = None
    instruction: Optional[str] = None
    enabled: bool = True


class RuleUpdate(BaseModel):
    rule_type: Optional[RuleType] = None
    value: Optional[str] = None
    severity: Optional[Severity] = None
    instruction: Optional[str] = None
    enabled: Optional[bool] = None
