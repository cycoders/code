from pydantic import BaseModel
from typing import List, Optional


class Issue(BaseModel):
    """Typed model for accessibility issues."""
    id: str
    wcag: str
    principle: str  # POUR: Perceivable, Operable, etc.
    level: str  # A, AA, AAA
    severity: str  # error, warning, info
    description: str
    impact: str
    help: str
    count: int = 1
    examples: List[str] = []


class AuditResult(BaseModel):
    """Summary of audit."""
    issues: List[Issue]
    score: str  # 'A' to 'F'
    total_checks: int
    violations: int
