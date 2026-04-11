from dataclasses import dataclass
from typing import Optional


@dataclass
class Request:
    timestamp: float
    duration: float
    status_code: int
    endpoint: str
    method: str
    error: Optional[str]
