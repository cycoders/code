import random
from retry_backoff_simulator.simulator import run_simulation
from retry_backoff_simulator.models import SimConfig, BackoffConfig


def test_run_simulation_success_immediate():
    config = SimConfig(
        backoff=BackoffConfig(base_delay=0.1, max_attempts=5, strategy="fixed"),
        failure_rate=0.0,
        service_time=0.01,
        num_trials=10,
        seed=42,
    )
    results = run_simulation(config)
    assert all(r.success for r in results)
    assert all(r.attempts == 1 for r in results)
    assert all(abs(r.total_time - 0.01) < 1e-6 for r in results)


def test_run_simulation_always_fail():
    config = SimConfig(
        backoff=BackoffConfig(base_delay=0.0, max_attempts=3, strategy="fixed"),
        failure_rate=1.0,
        num_trials=1,
    )
    results = run_simulation(config)
    assert not results[0].success
    assert results[0].attempts == 3


def test_failure_sequence():
    config = SimConfig(
        backoff=BackoffConfig(strategy="exponential"),
        failure_sequence=[True, False],
        num_trials=4,
        service_time=0.0,
    )
    results = run_simulation(config)
    # Cycle: fail, success, fail, success...
    assert results[0].attempts == 2
    assert results[0].success
    assert results[1].attempts == 1
    assert results[1].success


def test_seed_reproducible():
    config = SimConfig(num_trials=10, seed=42, failure_rate=0.5)
    results1 = run_simulation(config)
    results2 = run_simulation(config)
    assert results1 == results2
