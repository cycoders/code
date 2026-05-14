import pytest
from http3_tester_cli.metrics import compute_stats, percent_diff


def test_compute_stats():
    values = [10, 20, 30, 40, 50]
    stats = compute_stats(values)
    assert stats["mean"] == 30
    assert stats["p95"] == 47  # approx
    assert stats["min"] == 10


def test_percent_diff():
    assert percent_diff(120, 100) == 20
    assert percent_diff(100, 0) == 0
