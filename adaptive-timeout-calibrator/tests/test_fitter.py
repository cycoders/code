import pytest
from adaptive_timeout_calibrator.models import LatencyHistogram
from adaptive_timeout_calibrator.fitter import fit_and_recommend

def test_basic_fit():
    hist = LatencyHistogram(buckets_ms=[10, 50, 200], counts=[900, 90, 10])
    rec = fit_and_recommend(hist)
    assert rec.recommended_timeout_ms > 0
    assert rec.slo_compliant in (True, False)

def test_edge_empty():
    with pytest.raises(Exception):
        LatencyHistogram(buckets_ms=[], counts=[])

def test_high_tail():
    hist = LatencyHistogram(buckets_ms=list(range(10, 1000, 50)), counts=[100]*19 + [5])
    rec = fit_and_recommend(hist, slo=0.95)
    assert rec.p999_ms > rec.p99_ms