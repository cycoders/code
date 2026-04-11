import pytest
from loadtest_analyzer.stats import compute_stats, percentile
from loadtest_analyzer.models import Request


@pytest.fixture
 def sample_requests():
    return [
        Request(0.0, 100.0, 200, "/fast", "GET", None),
        Request(1.0, 200.0, 200, "/slow", "GET", None),
        Request(2.0, 150.0, 500, "/error", "POST", "boom"),
        Request(3.0, 120.0, 200, "/fast", "GET", None),
    ]

 def test_percentile():
    assert percentile([100, 150, 200], 50) == 150
    assert percentile([100, 150, 200], 95) == 200
    assert percentile([], 50) == 0.0

 def test_compute_stats(sample_requests):
    stats = compute_stats(sample_requests)
    assert stats["total_requests"] == 4
    assert stats["rps"] == 1.3333333333333333  # 4 / 3s
    assert stats["error_rate_pct"] == 25.0
    assert stats["avg_duration_ms"] == 142.5
    assert stats["p95_ms"] == 200.0
    assert len(stats["top_endpoints"]) == 2
    assert stats["top_endpoints"][0]["endpoint"] == "/slow"

 def test_empty_stats():
    assert compute_stats([]) == {}
