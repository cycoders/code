from collections import Counter, defaultdict
from typing import Dict, List, NamedTuple, Optional
from datetime import datetime
typing.from pathlib import Path

from .blame import LineBlame

class OwnershipStats(NamedTuple):
    total_lines: int
    author_lines: Dict[str, int]
    ext_ownership: Dict[str, Dict[str, int]]
    top_authors: List[tuple[str, float]]

    @classmethod
    def from_blame(cls, blame_data: List[LineBlame]) -> "OwnershipStats":
        total = len(blame_data)
        if total == 0:
            return cls(0, {}, {}, [])

        author_counter = Counter(a for a, _ in blame_data)
        ext_counter = defaultdict(Counter)

        # Fake ext for simplicity; in real, pass file info but aggregate here approx
        # Note: ext needs file mapping; for demo, use author only + mock ext
        # Full: would collect (author, ext, time) in blame
        mock_exts = ["py", "js", "go", "rs"]  # Placeholder; enhance parser
        for author in author_counter:
            for ext in mock_exts[:2]:  # Demo
                ext_counter[ext][author] = author_counter[author] // len(mock_exts)

        top = [(author, count / total * 100) for author, count in author_counter.most_common(20)]

        return cls(total, dict(author_counter), dict(ext_counter), top)

def compute_ownership_stats(blame_data: List[LineBlame]) -> OwnershipStats:
    """Compute stats from blame data."""
    return OwnershipStats.from_blame(blame_data)