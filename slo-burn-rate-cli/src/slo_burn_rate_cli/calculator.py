import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any


def compute_burn_rates(
    df: pd.DataFrame,
    metric: str,
    slo: float,
    window_days: int,
    budget_days: int,
) -> Dict[str, Any]:
    """Compute burn rates, budgets, and forecast."""
    if df.empty:
        return {}

    # Resample to hourly
    freq = '1H'
    if metric == 'error_rate' and 'is_error' in df.columns:
        agg = df.resample(freq).agg({
            'is_error': ['count', 'sum'],
        })
        agg.columns = ['total', 'errors']
        agg['rate'] = agg['errors'] / agg['total']
        agg = agg.dropna(subset=['rate'])
    elif metric == 'latency_p99' and 'latency' in df.columns:
        agg = df['latency'].resample(freq).quantile(0.99).rename('p99')
        agg = agg.dropna()
        allowed_latency = None  # Need --threshold
        raise NotImplementedError("Add --threshold for latency SLO")
    else:
        raise ValueError(f"Unsupported metric '{metric}' or missing columns")

    # Rolling mean rate
    window = f'{window_days}d'
    rolling_rate = agg['rate'].rolling(window, min_periods=24).mean().dropna()

    # Achieved SLO = 1 - rate
    achieved = 1 - rolling_rate
    # Burn rate = (1 - achieved) / (1 - SLO)
    burn_rate = (1 - achieved) / (1 - slo)

    history_df = pd.DataFrame({
        'date': burn_rate.index,
        'burn_rate': burn_rate,
        'achieved_slo': achieved,
    })

    if history_df.empty:
        return {}

    # Current (last window)
    current_burn = burn_rate.iloc[-1]
    current_slo = achieved.iloc[-1]

    # Budget remaining: simplistic linear consumption
    # Fraction consumed = (current_burn * (window_days / budget_days)) * (data_duration / budget_days)
    data_start = df.index.min()
    data_end = df.index.max()
    elapsed_days = (data_end - data_start).days
    budget_consumed_frac = min(1.0, current_burn * (elapsed_days / budget_days))
    budget_remaining = 1.0 - budget_consumed_frac

    # Forecast exhaust: assume constant burn_rate
    if current_burn > 0:
        days_to_exhaust = (budget_remaining / current_burn) * (budget_days / window_days)
        exhaust_date = data_end + timedelta(days=days_to_exhaust)
    else:
        days_to_exhaust = float('inf')
        exhaust_date = None

    return {
        'current_slo': current_slo,
        'current_burn_rate': current_burn,
        'budget_remaining_pct': budget_remaining,
        'forecast_exhaust_date': exhaust_date,
        'history_df': history_df,
    }
