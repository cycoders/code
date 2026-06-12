import numpy as np
from capacity_forecaster.models import linear_forecast, seasonal_forecast

def test_linear_forecast():
    series = np.array([10, 12, 14, 16])
    result = linear_forecast(series, 2)
    assert len(result) == 2
    assert result[0] > 16

def test_seasonal_forecast():
    series = np.sin(np.linspace(0, 4*np.pi, 28)) + 10
    result = seasonal_forecast(series, 7)
    assert len(result) == 7