from dataclasses import dataclass, asdict, field
from typing import Any, Dict, List


@dataclass
class DiffIssue:
    """Structured schema diff issue."""

    issue_type: str
    path: str
    description: str = ""
    old_value: Any = None
    new_value: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


DiffIssues = List[DiffIssue]