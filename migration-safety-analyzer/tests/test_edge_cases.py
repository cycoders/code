from migration_safety_analyzer.rules import is_destructive

def test_empty():
    assert not is_destructive('')