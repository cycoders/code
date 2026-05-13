import pytest
from load_balancer_simulator.simulator import run_simulation, compute_percentile
from load_balancer_simulator.config import Config


def test_compute_percentile():
    assert compute_percentile([1, 2, 3, 4], 50) == 2.0
    assert compute_percentile([1, 2, 3, 4], 75) == 3.0
    assert compute_percentile([], 50) == 0.0


def test_short_simulation(sample_config):
    results = run_simulation(sample_config)
    assert 'global' in results
    assert results['global']['total_reqs'] > 0
    assert 'backends' in results
    assert len(results['live_data']) > 0


def test_seed_reproducible(sample_config):
    sample_config.seed = 42
    results1 = run_simulation(sample_config)
    results2 = run_simulation(sample_config)
    assert results1['global']['total_reqs'] == results2['global']['total_reqs']