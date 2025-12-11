from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict
from enum import Enum

class AnonymizeMode(str, Enum):
    FAKE = "fake"
    HASH = "hash"
    REDACT = "redact"


@dataclass
class PIIColumnStats:
    column: str
    pii_percentage: float
    match_count: int
    dominant_type: Optional[str] = None


class Config(TypedDict):
    default_mode: AnonymizeMode
    threshold: float
    patterns: Dict[str, str]
    anonymizers: Dict[str, str]
    salt: Optional[str]
