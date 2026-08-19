from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class DDSketch:
    gamma: float = 1.015
    min_value: float = 1e-9
    max_value: float = 1e12
    counts: dict[int, int] = None

    def __post_init__(self):
        if self.counts is None:
            self.counts = {}

    def add(self, value: float, count: int = 1) -> None:
        if value < self.min_value:
            value = self.min_value
        bucket = int(math.log(value / self.min_value) / math.log(self.gamma))
        self.counts[bucket] = self.counts.get(bucket, 0) + count

    def merge(self, other: DDSketch) -> DDSketch:
        result = DDSketch(self.gamma, self.min_value, self.max_value)
        for b, c in {**self.counts, **other.counts}.items():
            result.counts[b] = result.counts.get(b, 0) + c
        return result

    def quantile(self, q: float) -> float:
        if not self.counts:
            return 0.0
        total = sum(self.counts.values())
        target = q * total
        acc = 0
        for b in sorted(self.counts):
            acc += self.counts[b]
            if acc >= target:
                return self.min_value * (self.gamma ** b)
        return self.max_value