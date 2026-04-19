from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Issue:
    severity: str  # error, warning, info
    code: str
    message: str
    path: List[str]
    suggestion: Optional[str] = None

    def __post_init__(self):
        if self.severity not in ("error", "warning", "info"):
            raise ValueError(f"Invalid severity: {self.severity}")
