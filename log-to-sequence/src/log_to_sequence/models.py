from typing import Optional, List, Dict

from pydantic import BaseModel

from datetime import datetime


class LogEntry(BaseModel):
    timestamp: datetime
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    service: str
    name: str
    duration_ms: Optional[float] = None


class Span(BaseModel):
    span_id: str
    service: str
    name: str
    duration_ms: Optional[float]
    start_ts: datetime
    children: List["Span"] = []


class Config(BaseModel):
    fields: Dict[str, str] = {
        "timestamp": "timestamp",
        "trace_id": "trace_id",
        "span_id": "span_id",
        "parent_span_id": "parent_span_id",
        "service": "service",
        "name": "name",
        "duration_ms": "duration_ms",
    }
    service_aliases: Dict[str, str] = {}