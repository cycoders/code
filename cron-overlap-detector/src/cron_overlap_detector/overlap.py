from datetime import datetime, timedelta
from typing import List, Tuple

class Interval:
    def __init__(self, start: datetime, end: datetime, job: str):
        self.start, self.end, self.job = start, end, job

def find_overlaps(intervals: List[Interval], tolerance: int = 60) -> List[Tuple[Interval, Interval]]:
    """O(n log n) overlap detection using sorted endpoints."""
    overlaps = []
    sorted_ints = sorted(intervals, key=lambda x: x.start)
    for i, a in enumerate(sorted_ints):
        for b in sorted_ints[i+1:]:
            if b.start - a.end > timedelta(seconds=tolerance):
                break
            overlaps.append((a, b))
    return overlaps