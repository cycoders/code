from dataclasses import dataclass
from typing import List, Optional


@dataclass
class StraceEvent:
    """Parsed strace event."""

    start_time: float
    pid: int
    syscall: str
    args: List[str]
    result: str
    duration: Optional[float]
    notes: Optional[str]
