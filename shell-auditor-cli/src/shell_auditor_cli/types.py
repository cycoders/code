from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class Issue:
    rule_id: str
    line: int
    column: int
    message: str
    severity: str  # info, low, medium, high, critical
    fix: Optional[str] = None


@dataclass
class AuditResult:
    path: Path
    issues: List[Issue]
    parse_errors: List[str] = None