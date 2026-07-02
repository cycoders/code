from migration_safety_analyzer.rules import is_destructive

def test_drop_is_destructive():
    assert is_destructive('DROP COLUMN id')