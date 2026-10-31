from __future__ import annotations

import numpy as np
from dataclasses import dataclass

@dataclass
class HDRHistogram:
    lowest_discernible: int = 1
    highest_trackable: int = 3600_000_000
    significant_digits: int = 3
    counts: np.ndarray | None = None

    def __post_init__(self):
        if self.counts is None:
            self.counts = np.zeros(4096, dtype=np.int64)

    def record(self, value: int, count: int = 1) -> None:
        if value <= 0:
            return
        idx = min(int(np.log2(value) * self.significant_digits), len(self.counts) - 1)
        self.counts[idx] += count

    def percentile(self, p: float) -> float:
        total = self.counts.sum()
        if total == 0:
            return 0.0
        target = total * p / 100
        cum = 0
        for i, c in enumerate(self.counts):
            cum += c
            if cum >= target:
                return 2 ** (i / self.significant_digits)
        return float(self.highest_trackable)