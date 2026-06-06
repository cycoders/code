import pytest
from bloom_filter_cli.calculator import optimal_params

def test_optimal_params_basic():
    m, k = optimal_params(1_000_000, 0.01)
    assert m > 0 and k > 0

def test_fp_bounds():
    with pytest.raises(ValueError):
        optimal_params(1000, 0)

def test_monotonic():
    m1, _ = optimal_params(10000, 0.001)
    m2, _ = optimal_params(10000, 0.01)
    assert m1 > m2