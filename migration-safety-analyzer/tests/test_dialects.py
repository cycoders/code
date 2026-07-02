from migration_safety_analyzer.dialects import lock_cost

def test_postgres_cost():
    assert lock_cost('postgres') > 1.0