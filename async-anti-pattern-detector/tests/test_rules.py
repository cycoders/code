from async_anti_pattern_detector.rules import RULES

def test_rule_registry():
    assert "BLOCKING_CALL" in RULES