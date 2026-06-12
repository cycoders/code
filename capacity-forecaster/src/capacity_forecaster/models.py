import numpy as np

def linear_forecast(series, horizon):
    x = np.arange(len(series))
    slope = np.polyfit(x, series, 1)[0]
    return series[-1] + slope * np.arange(1, horizon + 1)

def seasonal_forecast(series, horizon, period=7):
    # Simplified STL-like decomposition
    trend = np.convolve(series, np.ones(period)/period, mode='same')
    seasonal = series - trend
    forecast = trend[-1] + np.tile(seasonal[-period:], int(np.ceil(horizon/period)))[:horizon]
    return forecast