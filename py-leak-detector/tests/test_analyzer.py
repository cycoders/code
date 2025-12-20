import pytest
from py_leak_detector.analyzer import analyze_rss, analyze_heap_diffs
import tracemalloc


def test_analyze_rss_no_data():
    ana = analyze_rss([], [], 10)
    assert not ana.is_leak
    assert ana.max_delta_mb == 0


def test_analyze_rss_leak():
    rss = [50, 80, 120]
    ts = [0, 5, 10]
    ana = analyze_rss(rss, ts, 20)
    assert ana.is_leak
    assert ana.max_delta_mb == 40


def test_analyze_heap_no_snaps():
    ana = analyze_heap_diffs([], 1000)
    assert not ana.is_leak
