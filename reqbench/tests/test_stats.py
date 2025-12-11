import pytest
import numpy as np
from reqbench.stats import compute_stats


@pytest.mark.parametrize(
    "latencies, duration, total, errors, expected",
    [
        ([[1.0, 2.0, 3.0]], 1.0, 3, 0, {"p50": 2.0, "p95": 3.0, "rps": 3.0}),
        ([], 10.0, 0, 5, {"p50": 0.0, "error_rate": 0.0}),  # edge
        ([[0.1] * 100], 10.0, 100, 0, {"p95": 0.1, "rps": 10.0}),
    ],
)
def test_compute_stats(latencies, duration, total, errors, expected):
    stats = compute_stats(latencies, duration, total, errors)
    for k, v in expected.items():
        np.testing.assert_almost_equal(stats[k], v, decimal=1)