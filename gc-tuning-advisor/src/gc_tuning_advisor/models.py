from dataclasses import dataclass

@dataclass
class GCEvent:
    gen: int
    collected: int
    uncollectable: int
    duration_ms: float
    timestamp: float