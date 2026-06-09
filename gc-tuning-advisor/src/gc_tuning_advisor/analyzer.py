from collections import defaultdict
import statistics
from .models import GCEvent

def analyze(events: list[GCEvent]) -> dict:
    by_gen = defaultdict(list)
    for e in events:
        by_gen[e.gen].append(e.duration_ms)
    return {g: {'p95': statistics.quantiles(d, n=20)[18] if len(d) > 1 else max(d)} for g, d in by_gen.items()}