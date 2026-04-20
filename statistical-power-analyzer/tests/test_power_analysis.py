import pytest
import numpy as np
from statistical_power_analyzer.power_analysis import compute_power_analysis


@pytest.mark.parametrize("test_type, params, expected_nobs", [
    ("ttest-ind", {"effect_size": 0.5, "power": 0.8, "alpha": 0.05, "solve_for": "nobs"}, 63.77),
    ("prop-ztest", {"prop1": 0.05, "prop2": 0.07, "power": 0.8, "alpha": 0.05, "solve_for": "nobs"}, 31095.5),
    ("ttest-paired", {"effect_size": 0.5, "power": 0.8, "alpha": 0.05, "solve_for": "nobs"}, 26.43),
])
def test_compute_power_analysis(test_type, params, expected_nobs):
    params["test_type"] = test_type
    result = compute_power_analysis(**params)
    assert np.isclose(result["nobs1"], expected_nobs, atol=0.1)


def test_invalid_inputs():
    with pytest.raises(ValueError, match="alpha"):
        compute_power_analysis(test_type="ttest-ind", alpha=-0.1)
    with pytest.raises(ValueError, match="prop1"):
        compute_power_analysis(test_type="prop-ztest", power=0.8)


def test_mde_calculation():
    result = compute_power_analysis("ttest-ind", nobs1=100, power=0.8, alpha=0.05, solve_for="power")
    assert "mde" in result
    assert result["mde"] > 0
