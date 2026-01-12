from dataclasses import dataclass
from typing import Optional
from enum import Enum


class Status(str, Enum):
    PROPAGATED = "✅ Propagated"
    PENDING = "❌ Pending"
    ERROR = "⚠️ Error"


@dataclass
class PropagationResult:
    resolver_name: str
    ip: str
    location: str
    status: Status
    response: Optional[str] = None
    latency: float = 0.0
    error: Optional[str] = None