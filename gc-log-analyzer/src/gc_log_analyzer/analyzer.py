from typing import List
from .parser import GCPause

def compute_stats(pauses: List[GCPause]) -> dict:
    if not pauses:
        return {"total_pauses": 0}
    total = sum(p.duration_ms for p in pauses)
    max_p = max(p.duration_ms for p in pauses)
    return {
        "total_pauses": len(pauses),
        "total_time_ms": total,
        "max_pause_ms": max_p,
        "avg_pause_ms": total / len(pauses),
    }