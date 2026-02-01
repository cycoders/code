from dataclasses import dataclass, asdict
from typing import List


@dataclass
class Issue:
    """Represents a single audit issue."""
    resource: str = ""
    severity: str = "LOW"  # HIGH, MEDIUM, LOW
    message: str = ""
    field: str = ""
    suggestion: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


IssueList = List[Issue]