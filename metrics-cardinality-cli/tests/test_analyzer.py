from metrics_cardinality_cli.analyzer import estimate_cardinality

def test_detects_high_card():
    metrics = [{"name": "m", "labels": {"l": str(i)}} for i in range(1200)]
    res = estimate_cardinality(metrics, 1000)
    assert res[0]["cardinality"] == 1200

def test_severity_tiers():
    metrics = [{"name": "m", "labels": {"l": str(i)}} for i in range(6000)]
    res = estimate_cardinality(metrics, 1000)
    assert res[0]["severity"] == "high"

def test_empty_input():
    assert estimate_cardinality([], 1000) == []