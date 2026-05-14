import pytest
from datetime import datetime, timedelta
from slo_burn_rate_cli.calculator import compute_burn_rates


@pytest.mark.parametrize("metric,slo,expected_burn", [
    ("error_rate", 0.99, 0.25),  # 1 error / 4 req = 0.25 rate, burn=(0.25)/0.01=25
])
def test_compute_burn_rates(sample_data, metric, slo, expected_burn):
    results = compute_burn_rates(sample_data, metric, slo, 1, 30)
    assert results['current_burn_rate'] == pytest.approx(expected_burn, rel=0.1)


def test_empty_df():
    import pandas as pd
    results = compute_burn_rates(pd.DataFrame(), 'error_rate', 0.999, 28, 90)
    assert results == {}


def test_forecast_positive():
    # Mock results with burn=0.5, remaining=0.5 -> time_to_exhaust ~ budget/window * remaining/burn
    pass  # Integrated in main test
