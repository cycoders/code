from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


class NetlogEvent(BaseModel):
    """Parsed Chrome netlog event."""

    source_type: str
    source: Dict[str, Any]
    type: str
    time: float  # microseconds since epoch
    params: Dict[str, Any]


class PriorityInfo(BaseModel):
    """HTTP/2 stream priority details."""

    dependency: int = 0
    weight: int = 201
    exclusive: bool = False


class Stream(BaseModel):
    """Aggregated HTTP/2 stream data."""

    id: int
    url: Optional[str] = None
    priority: PriorityInfo
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None
    content_type: Optional[str] = None

    @property
    def name(self) -> str:
        return self.url or f"Stream-{self.id}"


@dataclass
class BlockingChain:
    streams: list[int]
    total_block_ms: float
