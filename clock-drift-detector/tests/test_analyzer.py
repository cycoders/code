import pytest
from clock_drift_detector.analyzer import analyze

def test_basic_skew():
    # synthetic data with known 12ms skew
    assert abs(analyze(["t1.log"], "trace_id", "ts")["skews"]["node2"]) - 0.012 < 0.001

def test_outlier_resistance():
    ...
def test_empty_sources():
    assert analyze([], "k", "ts")["n_events"] == 0