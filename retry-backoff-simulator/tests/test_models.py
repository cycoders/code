import pytest
from pydantic import ValidationError

from retry_backoff_simulator.models import (
    SimConfig,
    BackoffConfig,
    aggregate_metrics,
    TrialResult,
    percentile,
)


def test_backoff_config_validation():
    config = BackoffConfig(base_delay=0.1, strategy="full_jitter")
    assert config.strategy == "full_jitter"

    with pytest.raises(ValidationError):
        BackoffConfig(base_delay=-0.1)

    with pytest.raises(ValidationError):
        BackoffConfig(strategy="invalid")


def test_sim_config_validation():
    config = SimConfig(failure_rate=0.7, num_trials=100)
    assert config.failure_rate == 0.7


def test_percentile_edge_cases():
    assert percentile([], 50) == 0.0
    assert percentile([1, 2, 3], 50) == 2.0
    assert 2.5 <= percentile([1, 2, 3, 4], 50) <= 2.5
    assert percentile([5], 95) == 5.0


def test_aggregate_metrics():
    results = [
        TrialResult(total_time=1.0, attempts=1, success=True),
        TrialResult(total_time=2.5, attempts=3, success=True),
        TrialResult(total_time=10.0, attempts=10, success=False),
    ]
    metrics = aggregate_metrics(results)
    assert abs(metrics.success_rate - 2/3) < 1e-6
    assert metrics.avg_attempts == (1 + 3 + 10) / 3
    assert metrics.p95_time >= 10.0
