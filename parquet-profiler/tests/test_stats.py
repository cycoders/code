import pyarrow.dataset as ds
import pytest
from parquet_profiler.stats import compute_stats, NumericAccumulator, StringAccumulator
from parquet_profiler.types import ColumnStats


def test_numeric_accumulator(sample_parquet):
    dataset = ds.dataset(sample_parquet)
    stats = compute_stats(dataset, "salary", 10)
    assert stats.count == 4
    assert stats.null_count == 1
    assert stats.null_pct == 20.0
    assert stats.min_val == 50000.0
    assert stats.max_val == 70000.0
    assert 60000 <= stats.mean <= 61250


def test_string_accumulator(sample_parquet):
    dataset = ds.dataset(sample_parquet)
    stats = compute_stats(dataset, "name", 10)
    assert stats.count == 4
    assert stats.null_count == 1
    assert stats.distinct_approx == 3
    assert stats.top_values["Alice"] == 50.0


def test_histogram():
    from parquet_profiler.stats import _ascii_histogram
    hist = _ascii_histogram([1,2,2,3,100])
    assert "█" in hist
    assert len(hist.split("\n")) == 20


def test_quality_alerts(sample_parquet):
    dataset = ds.dataset(sample_parquet)
    stats = compute_stats(dataset, "name", 10)
    assert "High null ratio" not in stats.quality_alerts  # 20%
