import pytest
from collections import Counter
from har_analyzer.analyzer import (
    compute_stats,
    top_slow,
    domains,
    resource_types,
    detect_anomalies,
)


class TestAnalyzer:
    def test_compute_stats_empty(self, sample_entries):
        stats = compute_stats([])
        assert stats["total_requests"] == 0
        assert stats["avg_response_time"] == 0
        assert stats["p95_time"] == 0
        assert stats["error_rate_pct"] == 0

    def test_compute_stats(self, sample_entries):
        stats = compute_stats(sample_entries)
        assert stats["total_requests"] == 5
        assert stats["avg_response_time"] > 0
        assert stats["p95_time"] >= stats["avg_response_time"]

    def test_top_slow(self, sample_entries):
        slow = top_slow(sample_entries, n=2)
        assert len(slow) == 2
        assert slow[0]["time"] >= slow[1]["time"]

    def test_domains(self, sample_entries):
        doms = domains(sample_entries)
        assert isinstance(doms, Counter)
        assert len(doms) > 0

    def test_resource_types(self, sample_entries):
        types = resource_types(sample_entries)
        assert isinstance(types, Counter)
        assert "text/html" in types or "application/json" in types

    def test_detect_anomalies(self, sample_entries):
        anoms = detect_anomalies(sample_entries)
        assert isinstance(anoms, list)
        # Add slow/large entry in sample to trigger