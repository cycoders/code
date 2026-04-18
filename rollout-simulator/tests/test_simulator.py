import numpy as np  # type: ignore
import pytest
from rollout_simulator.types import DeployMetrics, SimResult
from rollout_simulator.simulator import run_simulation
from rollout_simulator.metrics import compute_error_deltas


@pytest.fixture
def stable_deploys():
    return [
        DeployMetrics(deploy_id="v1", avg_error_rate=0.01, std_error_rate=0.001, num_entries=10, first_ts=..., last_ts=...),  # type: ignore
        DeployMetrics(deploy_id="v2", avg_error_rate=0.012, std_error_rate=0.001, num_entries=10, first_ts=..., last_ts=...),  # type: ignore
    ]


def test_compute_error_deltas(stable_deploys):
    deltas = compute_error_deltas(stable_deploys)
    assert np.allclose(deltas, [0.002])


def test_run_simulation(stable_deploys):
    result = run_simulation(stable_deploys, [100], "test", 0.015, num_sims=100)
    assert isinstance(result, SimResult)
    assert 0 <= result.risk_pct <= 100
    # High risk since delta=+0.002 -> 0.014 <0.015? Wait, adjust
    assert result.steps == [100]