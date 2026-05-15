from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class KeyInfo:
    key_type: str
    size_bits: Optional[int]
    curve: Optional[str]
    fingerprint: str
    comment: Optional[str]


@dataclass
class Issue:
    file_path: str
    line_num: int
    key_info: KeyInfo
    issue_type: str
    message: str
    severity: Severity
