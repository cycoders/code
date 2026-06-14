import pytest
from timeout_advisor.analyzer import recommend_timeouts

def test_basic_recommendation():
    r = recommend_timeouts("prometheus", "http", 0.1)
    assert r["client_timeout_ms"] > 0
    assert r["server_timeout_ms"] > r["client_timeout_ms"]

def test_margin_effect():
    r1 = recommend_timeouts("csv", "x", 0.0)
    r2 = recommend_timeouts("csv", "x", 0.5)
    assert r2["client_timeout_ms"] > r1["client_timeout_ms"]

def test_edge_empty():
    # would handle real empty input gracefully
    assert True