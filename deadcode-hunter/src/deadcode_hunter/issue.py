from dataclasses import dataclass
from typing import Any


@dataclass
class Issue:
    """Represents a detected deadcode issue."""

    file_path: str
    line_no: int
    col_offset: int
    name: str
    issue_type: str  # 'unused_import', 'unused_function', 'unused_class', 'unused_variable'
    confidence: int  # 0-100
    description: str

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 100:
            raise ValueError("Confidence must be 0-100")

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "line_no": self.line_no,
            "col_offset": self.col_offset,
            "name": self.name,
            "issue_type": self.issue_type,
            "confidence": self.confidence,
            "description": self.description,
        }