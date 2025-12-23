import pytest
from perf_guard.stats import compute_stats, is_regression, format_duration


def test_compute_stats():
    times = [1.0, 1.2, 0.8]
    stats = compute_stats(times)
    assert stats["mean"] == 1.0
    assert stats["iterations"] == 3
    assert stats["min"] == 0.8
    assert stats["max"] == 1.2
    assert pytest.approx(stats["stdev"], abs=0.2) == 0.14142


def test_compute_stats_single():
    stats = compute_stats([1.0])
    assert stats["stdev"] == 0.0


def test_compute_stats_empty():
    with pytest.raises(ValueError, match="No valid"):
        compute_stats([])


def test_is_regression():
    old = compute_stats([1.0] * 10)
    new_fast = compute_stats([0.9] * 10)
    new_slow = compute_stats([1.2] * 10)

    assert not is_regression(old, new_fast, 0.1)
    assert is_regression(old, new_slow, 0.1)


def test_format_duration():
    assert format_duration(0.00123) == "1.230ms"
    assert format_duration(0.000123) == "123.000μs"
    assert format_duration(1.23) == "1.230s"
    assert format_duration(0) == "0s"