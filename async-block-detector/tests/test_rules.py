from async_block_detector.rules import BLOCKING_CALLS

def test_core_blockers_present():
    assert "sleep" in BLOCKING_CALLS
    assert "get" in BLOCKING_CALLS

def test_no_false_positives():
    assert "gather" not in BLOCKING_CALLS