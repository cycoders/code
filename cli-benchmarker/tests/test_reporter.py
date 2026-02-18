import pytest
from cli_benchmarker.reporter import compute_stats, make_sparkline, percentile


class TestPercentile:
    def test_p95(self):
        times = [1.0, 1.1, 1.2, 2.0, 3.0]
        assert percentile(times, 0.95) == 3.0  # approx

    def test_empty(self):
        assert percentile([], 0.95) == 0.0


class TestSparkline:
    def test_constant(self):
        assert "█" in make_sparkline([1.0, 1.0, 1.0])

    def test_varied(self):
        spark = make_sparkline([1, 2, 3, 10])
        assert len(spark) == 30
        assert "█" in spark

    def test_empty(self):
        assert make_sparkline([]).startswith("▁")


class TestComputeStats:
    def test_success(self):
        results = [
            {"success": True, "wall_time": 1.0, "cpu_total": 0.5, "mem_peak_mb": 100},
            {"success": True, "wall_time": 1.2, "cpu_total": 0.6, "mem_peak_mb": 110},
            {"success": False, "wall_time": 10, "cpu_total": 0, "mem_peak_mb": 0},
        ]
        stats = compute_stats(results)
        assert stats["n_success"] == 2
        assert stats["n_failed"] == 1
        assert abs(stats["wall_mean"] - 1.1) < 0.1

    def test_all_fail(self):
        results = [{"success": False, "wall_time": 10}]
        stats = compute_stats(results)
        assert "error" in stats