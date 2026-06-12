import numpy as np

def monte_carlo(base_forecast, n_runs=10000, noise=0.05, seed=42):
    rng = np.random.default_rng(seed)
    runs = [base_forecast * (1 + rng.normal(0, noise, len(base_forecast))) for _ in range(n_runs)]
    return np.percentile(runs, [5, 50, 95], axis=0)