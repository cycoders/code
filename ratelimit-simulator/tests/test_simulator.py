import pytest
import math
from ratelimit_simulator.simulator import (
    generate_requests,
    run_simulation,
    SimulationConfig,
)


@pytest.fixture
def base_config():
    return SimulationConfig(
        duration=10.0,
        rps=10.0,
        num_keys=1,
        policy_name="fixed",
        policy_params={"limit": 100, "window": 10.0},
    )


def test_generate_requests(base_config):
    reqs = generate_requests(base_config.duration, base_config.rps, base_config.num_keys)
    assert len(reqs) > 80  # ~100 expected
    assert all(t >= 0 and t <= base_config.duration for t, _ in reqs)
    keys = {k for _, k in reqs}
    assert len(keys) <= base_config.num_keys


@pytest.mark.parametrize("rps, expected_len_approx", [(0, 0), (1, (5, 15)), (100, (800, 1200))])
def test_poisson_rate(rps, expected_len_approx):
    reqs = generate_requests(10.0, rps, 1)
    n = len(reqs)
    assert expected_len_approx[0] <= n <= expected_len_approx[1]


def test_run_simulation_high_limit(base_config):
    base_config.policy_params["limit"] = 1000
    stats = run_simulation(base_config)
    assert stats.hit_rate > 0.99
    assert stats.total_requests > 80


def test_run_simulation_low_limit(base_config):
    base_config.policy_params["limit"] = 1
    base_config.rps = 2.0
    stats = run_simulation(base_config)
    assert stats.hit_rate < 0.8
    assert stats.max_burst == 1


def test_zero_rps(base_config):
    base_config.rps = 0
    stats = run_simulation(base_config)
    assert stats.total_requests == 0
    assert stats.hit_rate == 0.0
