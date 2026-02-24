from __future__ import annotations

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class LogRecord(BaseModel):
    timestamp: int = Field(..., description="Unix timestamp in microseconds")
    fields: List[Dict[str, Any]] = Field(default_factory=list)


class Span(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    traceID: str = Field(..., description="Hex trace identifier")
    spanID: str = Field(..., description="Hex span identifier")
    parentSpanID: Optional[str] = Field(None, description="Parent span ID")
    operationName: str = Field(..., description="Span name")
    startTime: int = Field(..., description="Unix µs")
    duration: int = Field(..., description="Duration in µs")
    tags: Dict[str, str] = Field(default_factory=dict)
    logs: List[LogRecord] = Field(default_factory=list)

    @property
    def service(self) -> str:
        """Extract service name from tags."""
        return self.tags.get("service.name", "unknown")

    @property
    def is_error(self) -> bool:
        """Check if span has error tag."""
        return self.tags.get("error", "false").lower() == "true"

    @property
    def start_time_sec(self) -> float:
        """Start time in seconds."""
        return self.startTime / 1_000_000.0

    @property
    def duration_sec(self) -> float:
        """Duration in seconds."""
        return self.duration / 1_000_000.0

    @property
    def end_time_sec(self) -> float:
        """End time in seconds."""
        return self.start_time_sec + self.duration_sec
