from dataclasses import dataclass
from typing import Dict, List
import numpy as np
from scipy import stats

@dataclass
class DiffResult:
    regressions: List[dict]
    improvements: List[dict]
    total_delta: int

def compute_diff(before: Dict[str, int], after: Dict[str, int], alpha: float) -> DiffResult:
    """Compute per-frame statistical differences."""
    all_frames = set(before) | set(after)
    regressions, improvements = [], []
    total_delta = 0
    for frame in all_frames:
        b = before.get(frame, 0)
        a = after.get(frame, 0)
        delta = a - b
        total_delta += delta
        if abs(delta) < 5:
            continue
        # bootstrap significance
        samples_b = np.random.choice([0, 1], size=1000, p=[1-b/(b+1), b/(b+1)])
        samples_a = np.random.choice([0, 1], size=1000, p=[1-a/(a+1), a/(a+1)])
        _, p = stats.mannwhitneyu(samples_b, samples_a, alternative='two-sided')
        item = {'frame': frame, 'delta': delta, 'p': p}
        if p < alpha and delta > 0:
            regressions.append(item)
        elif p < alpha and delta < 0:
            improvements.append(item)
    return DiffResult(regressions, improvements, total_delta)