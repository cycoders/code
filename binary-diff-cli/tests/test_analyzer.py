import math
from collections import Counter

import pytest
from binary_diff_cli.analyzer import (
    entropy,
    byte_histogram,
    compute_stats,
    entropy_bars,
)


class TestEntropy:
    def test_entropy_zero(self):
        assert entropy(Counter(), 0) == 0.0

    def test_entropy_uniform(self):
        hist = Counter({0: 1, 1: 1})
        assert math.isclose(entropy(hist, 2), 1.0)

    def test_entropy_skewed(self):
        hist = Counter({"a": 90, "b": 10})
        assert math.isclose(entropy(hist, 100), 0.469)


class TestByteHistogram:
    def test_sample_limit(tmp_path):
        f = tmp_path / "big.bin"
        f.write_bytes(b"a" * 2**20)
        hist = byte_histogram(f, sample_size=1000)
        assert sum(hist.values()) == 1000
        assert hist[b"a"] == 1000


class TestComputeStats(tmp_bins):
    @pytest.mark.parametrize("sample_bytes", [100, None])
    def test_changed_pct(self, tmp_bins, sample_bytes):
        f1, f2, _, _ = tmp_bins
        stats = compute_stats(f1, f2, sample_bytes)
        assert stats["changed"] == 20
        assert math.isclose(stats["change_pct"], 20 / 90)

    def test_diff_sizes(self, tmp_bins):
        f1, _, f_short, _ = tmp_bins
        stats = compute_stats(f1, f_short, 100)
        assert stats["size_delta"] > 0
        assert stats["changed"] == 0  # first 30 bytes same


class TestEntropyBars:
    def test_empty(self, tmp_path):
        f = tmp_path / "empty"
        f.touch()
        bars = entropy_bars(f)
        assert "empty" in bars

    def test_constant(self, tmp_path):
        f = tmp_path / "const"
        f.write_bytes(b"\x00" * 4096)
        plot = entropy_bars(f)
        assert "░" * 20 in plot  # low entropy
