import numpy as np
from capacity_forecaster.simulation import monte_carlo

def test_monte_carlo_shape():
    base = np.arange(10)
    p = monte_carlo(base, n_runs=100)
    assert p.shape == (3, 10)
    assert p[0][0] < p[2][0]