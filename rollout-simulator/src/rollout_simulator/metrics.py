import numpy as np  # type: ignore
from typing import List
from .types import DeployMetrics


def compute_error_deltas(deploys: List[DeployMetrics]) -> np.ndarray:
    """Compute empirical error rate deltas between consecutive deploys."""
    if len(deploys) < 2:
        return np.array([0.0])
    deltas = np.array([
        deploys[i + 1].avg_error_rate - deploys[i].avg_error_rate
        for i in range(len(deploys) - 1)
    ])
    return deltas