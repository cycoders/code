from error_budget_cli.calculator import remaining_budget, burn_rate, hours_to_exhaustion

def test_remaining_budget():
    assert remaining_budget(99.9, 100000, 50) == 50.0

def test_burn_rate():
    assert burn_rate(10, 1000, 3600) == 0.01

def test_exhaustion():
    assert hours_to_exhaustion(100, 2.0) == 50.0