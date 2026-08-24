from copyleft_risk_analyzer.propagator import propagate

def test_no_obligations():
    assert propagate({}, {}) == []