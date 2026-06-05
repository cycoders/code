from context_manager_linter.registry import DEFAULT_RESOURCES

def test_contains_core_resources():
    assert "open" in DEFAULT_RESOURCES
    assert "Lock" in DEFAULT_RESOURCES