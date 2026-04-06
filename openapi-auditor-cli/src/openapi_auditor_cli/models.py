from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Issue:
    """Represents an audit issue."""
    path: List[str]
    rule_id: str
    message: str
    severity: str  # 'error', 'warn', 'info'
    suggestion: Optional[str] = None

    def __post_init__(self):
        if self.severity not in ('error', 'warn', 'info'):
            raise ValueError(f"Invalid severity: {self.severity}")
