from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    def __str__(self) -> str:
        return self.value


@dataclass
class Issue:
    """Represents an audit issue."""

    file: str
    """Path to the workflow file."""

    rule: str
    """Rule ID."""

    message: str
    """Human-readable description."""

    severity: Severity
    """Issue severity."""

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity.value,
        }
