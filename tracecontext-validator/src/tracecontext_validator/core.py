import re
from dataclasses import dataclass
from typing import Optional

TRACEPARENT_RE = re.compile(r"^(\d{2})-([0-9a-f]{32})-([0-9a-f]{16})-(\d{2})$")

@dataclass
class TraceContext:
    version: str
    trace_id: str
    parent_id: str
    flags: str
    valid: bool
    error: Optional[str] = None

def parse_traceparent(header: str) -> TraceContext:
    header = header.strip()
    m = TRACEPARENT_RE.match(header)
    if not m:
        return TraceContext("00", "", "", "00", False, "invalid format")
    version, trace_id, parent_id, flags = m.groups()
    if version == "ff" or trace_id == "0" * 32 or parent_id == "0" * 16:
        return TraceContext(version, trace_id, parent_id, flags, False, "reserved value used")
    return TraceContext(version, trace_id, parent_id, flags, True)