import numpy as np
import pytest
from ab_test_calculator_cli.stats import (
    design_proportion,
    design_mean,
    analyze_proportion,
)


@pytest.mark.parametrize(
    "baseline,mde,alpha,power,ratio,expected_n_a",
    [
        (0.5, 0.1, 0.05, 0.8, 1.0, 392),  # Standard
        (0.05, 0.01, 0.05, 0.8, 1.0, 15708),
        (0.05, 0.01, 0.05, 0.8, 2.0, 15708),
        (0.01, 0.002, 0.01, 0.9, 1.0, 94489),
    ],
)
def test_design_proportion(baseline, mde, alpha, power, ratio, expected_n_a):
    result = design_proportion(baseline, mde, alpha, power, ratio)
    assert result.n_a == expected_n_a
    assert result.n_b == int(np.ceil(expected_n_a * ratio))


@pytest.mark.parametrize(
    "baseline,mde,stddev,alpha,power,ratio,expected_n_a",
    [
        (100, 10, 50, 0.05, 0.8, 1.0, 98),  # Cohen's d=0.2
        (100, 5, 20, 0.05, 0.8, 1.0, 338),
    ],
)
def test_design_mean(baseline, mde, stddev, alpha, power, ratio, expected_n_a):
    result = design_mean(baseline, mde, stddev, alpha, power, ratio)
    assert result.n_a == expected_n_a


@pytest.mark.parametrize(
    "a_s,b_s,a_t,b_t,alpha,prior,p_b_sup",
    [
        (100, 100, 1000, 1000, 0.05, 1.0, 0.5),  # Equal
        (100, 120, 1000, 1000, 0.05, 1.0, ~0.78),  # Approx
        (0, 0, 10, 10, 0.05, 0.5, 0.5),  # Zero
    ],
)
def test_analyze_proportion(a_s, b_s, a_t, b_t, alpha, prior, p_b_sup):
    tol = 0.05 if p_b_sup == "~0.78" else 0.01
    result = analyze_proportion(a_s, a_t, b_s, b_t, alpha, prior)
    assert 0 <= result.p_value <= 1
    assert result.ci_a[0] <= result.ci_a[1]
    np.testing.assert_allclose(result.prob_b_superior, p_b_sup, atol=tol)


def test_analyze_warning_low_events():
    result = analyze_proportion(1, 5, 2, 5)
    assert "Low event counts" in result.warning


def test_bayes_zero():
    result = analyze_proportion(0, 10, 0, 10)
    assert result.warning is None  # Priors handle
    assert abs(result.prob_b_superior - 0.5) < 0.01