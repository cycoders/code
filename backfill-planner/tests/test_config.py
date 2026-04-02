import pytest
from backfill_planner.config import BackfillConfig, Strategy


def test_config_validation(sample_config_dict):
    config = BackfillConfig(**sample_config_dict)
    assert config.total_rows == 1000000
    assert config.strategy == Strategy.ONLINE_BATCHED


def test_invalid_throughput():
    invalid = {"write_throughput_avg": 100, "write_throughput_min": 10000}
    with pytest.raises(ValueError):
        BackfillConfig(table="t", total_rows=1, **invalid)


def test_large_row_size():
    with pytest.raises(ValueError):
        BackfillConfig(table="t", total_rows=1, row_size_bytes=2000000, write_throughput_avg=1)
