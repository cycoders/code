import pytest
from backfill_planner.config import BackfillConfig
from backfill_planner.estimator import optimal_batch_size, estimate_phase_time


def test_optimal_batch_size(sample_config_dict):
    config = BackfillConfig(**sample_config_dict)
    batch = optimal_batch_size(config)
    assert 10000 <= batch <= 100000  # throughput*60=60k, mem~4M rows


def test_estimate_phase_time():
    time = estimate_phase_time(1000000, 1000.0)
    assert time == 1200  # 1000s *1.2 =1200


def test_num_batches():
    from backfill_planner.estimator import num_batches
    assert num_batches(1000000, 250000) == 4
