from typing import List, Dict, Any, Tuple, NamedTuple
from rich.console import Console
import tracemalloc

class RSSAnalysis(NamedTuple):
    history_mb: List[float]
    timestamps: List[float]
    deltas_mb: List[float]
    max_delta_mb: float
    avg_delta_mb_per_s: float
    total_growth_mb: float
    is_leak: bool

class HeapLeak(NamedTuple):
    size_diff: int
    count_diff: int
    location: str

class HeapAnalysis(NamedTuple):
    leaks: List[HeapLeak]
    is_leak: bool


def analyze_rss(
    rss_mb: List[float],
    timestamps: List[float],
    threshold_mb: float,
) -> RSSAnalysis:
    if len(rss_mb) < 2:
        return RSSAnalysis([], [], [], 0, 0, 0, False)

    deltas_mb = [rss_mb[i+1] - rss_mb[i] for i in range(len(rss_mb)-1)]
    elapsed = timestamps[-1] - timestamps[0] if timestamps else 0
    avg_delta_per_s = (sum(deltas_mb) / elapsed) if elapsed > 0 else 0
    max_delta = max(deltas_mb, default=0)
    total_growth = rss_mb[-1] - rss_mb[0]
    is_leak = max_delta > threshold_mb

    return RSSAnalysis(rss_mb, timestamps, deltas_mb, max_delta, avg_delta_per_s, total_growth, is_leak)


def analyze_heap_diffs(
    snapshots: List[tracemalloc.Snapshot],
    threshold_bytes: int,
) -> HeapAnalysis:
    leaks = []
    for i in range(1, len(snapshots)):
        diff_stats = snapshots[i].compare_to(snapshots[i-1], "lineno")
        for stat in diff_stats:
            if stat.size_diff > threshold_bytes:
                frame = stat.traceback[0]
                loc = f"{Path(frame.filename).name}:{frame.lineno} in {frame.name}"
                leaks.append(HeapLeak(stat.size_diff, stat.count_diff, loc))
    leaks.sort(key=lambda l: l.size_diff, reverse=True)
    is_leak = bool(leaks)
    return HeapAnalysis(leaks[:20], is_leak)  # top 20
