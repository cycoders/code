from slo_burn_rate_cli.viz import render_results
import pandas as pd
from unittest.mock import Mock


def test_render_table(capfd):
    results = {
        'current_slo': 0.997,
        'current_burn_rate': 1.2,
        'budget_remaining_pct': 0.3,
        'forecast_exhaust_date': pd.Timestamp.now() + pd.Timedelta(days=30),
        'history_df': pd.DataFrame({'date': [], 'burn_rate': []}),
    }
    console = Mock()
    render_results(results, 'table', console)
    captured = capfd.readouterr()
    assert 'Burn Rate' in captured.out


def test_render_json(capfd):
    results = {'history_df': pd.DataFrame({'a': [1]}), **{}}
    render_results(results, 'json', Mock())
    captured = capfd.readouterr()
    assert '[' in captured.out  # JSON array
