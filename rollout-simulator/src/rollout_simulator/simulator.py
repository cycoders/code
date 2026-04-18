import numpy as np  # type: ignore
from typing import List

from .types import DeployMetrics, SimResult
from .metrics import compute_error_deltas


def run_simulation(
    deploys: List[DeployMetrics],
    steps: List[int],
    name: str,
    threshold: float,
    num_sims: int = 1000,
) -> SimResult:
    """Run Monte-Carlo sim for strategy risk."""
    baseline = deploys[-1].avg_error_rate if deploys else 0.0
    deltas = compute_error_deltas(deploys)

    rng = np.random.default_rng()
    max_errors = np.zeros(num_sims)
    for i in range(num_sims):
        delta = rng.choice(deltas)
        new_error = baseline + delta
        step_max = max(
            (100 - s) / 100 * baseline + s / 100 * new_error
            for s in steps
        )
        max_errors[i] = step_max

    risk_pct = np.mean(max_errors > threshold) * 100
    return SimResult(
        strategy_name=name,
        steps=steps,
        risk_pct=float(risk_pct),
        p95_max_error=float(np.percentile(max_errors, 95)),
        avg_max_error=float(np.mean(max_errors)),
    )