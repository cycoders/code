from dataclasses import dataclass
from typing import Optional


@dataclass
class SlowQuery:
    timestamp: str
    duration_ms: float
    user: str
    database: str
    query: str
    host: Optional[str] = None
    client_pid: Optional[str] = None
