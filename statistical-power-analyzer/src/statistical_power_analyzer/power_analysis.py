from typing import Dict, Any, Optional, Union
import numpy as np
from statsmodels.stats.power import TTestIndPower, TTestPower, NormalIndPower, FTestAnovaPower
from statsmodels.stats.proportion import proportion_effectsize


def compute_power_analysis(
    test_type: str,
    effect_size: Optional[float] = None,
    nobs1: Optional[float] = None,
    power: Optional[float] = None,
    alpha: float = 0.05,
    ratio: float = 1.0,
    alternative: str = "two-sided",
    prop1: Optional[float] = None,
    prop2: Optional[float] = None,
    solve_for: str = "power",
) -> Dict[str, Any]:
    """Compute power analysis for various tests. Returns dict with solved values."""
    _validate_inputs(alpha, power, effect_size, nobs1)

    if test_type == "prop-ztest":
        if prop1 is None or prop2 is None:
            raise ValueError("prop1 and prop2 required for prop-ztest")
        effect_size = proportion_effectsize(prop1, prop2, method="normal")
        power_obj = NormalIndPower()
        solve_result = _solve_generic(power_obj, effect_size, nobs1, power, alpha, ratio, alternative, solve_for)
        solve_result["prop1"] = prop1
        solve_result["prop2"] = prop2
        return solve_result

    elif test_type == "ttest-ind":
        power_obj = TTestIndPower()
        return _solve_generic(power_obj, effect_size, nobs1, power, alpha, ratio, alternative, solve_for)

    elif test_type == "ttest-paired":
        power_obj = TTestPower()
        # Paired uses nobs (not nobs1), no ratio
        solve_result = _solve_paired(power_obj, effect_size, nobs1, power, alpha, alternative, solve_for)
        solve_result["nobs2"] = solve_result["nobs1"]  # Equal
        solve_result["ratio"] = 1.0
        return solve_result

    elif test_type == "anova-2":
        power_obj = FTestAnovaPower()
        k_groups = 2
        return _solve_generic(power_obj, effect_size, nobs1, power, alpha, ratio=1.0, alternative=None, solve_for=solve_for, k_groups=k_groups)

    else:
        raise ValueError(f"Unknown test_type: {test_type}")


def _validate_inputs(alpha: float, power: Optional[float], effect_size: Optional[float], nobs1: Optional[float]):
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    if power is not None and not 0 < power <= 1:
        raise ValueError("power must be between 0 and 1")
    if effect_size is not None and effect_size <= 0:
        raise ValueError("effect_size must be > 0")
    if nobs1 is not None and nobs1 <= 0:
        raise ValueError("nobs1 must be > 0")


def _solve_generic(
    power_obj,
    effect_size: float,
    nobs1: Optional[float],
    power: Optional[float],
    alpha: float,
    ratio: float,
    alternative: str,
    solve_for: str,
    **kwargs
):
    """Generic solver: set target param to None and solve."""
    params = {
        "effect_size": effect_size,
        "nobs1": nobs1,
        "power": power,
        "alpha": alpha,
    }
    if solve_for in params:
        params[solve_for] = None

    solved = power_obj.solve_power(
        effect_size=params["effect_size"],
        nobs1=params["nobs1"],
        alpha=params["alpha"],
        power=params["power"],
        ratio=ratio,
        alternative=alternative,
        **kwargs
    )

    result = params.copy()
    result[solve_for] = solved
    result["nobs2"] = result["nobs1"] * ratio if result["nobs1"] else None
    result["ratio"] = ratio
    result["alternative"] = alternative

    # Compute MDE if solving for power or nobs
    if solve_for in ["power", "nobs"]:
        result["mde"] = _compute_mde(power_obj, result["nobs1"], result["power"], alpha, ratio, alternative)

    return result


def _solve_paired(power_obj, effect_size, nobs, power, alpha, alternative, solve_for):
    params = {"effect_size": effect_size, "nobs": nobs, "power": power, "alpha": alpha}
    if solve_for == "nobs":
        params["nobs"] = None
    elif solve_for == "power":
        params["power"] = None
    elif solve_for == "effect_size":
        params["effect_size"] = None

    solved = power_obj.solve_power(
        effect_size=params["effect_size"],
        nobs=params["nobs"],
        alpha=params["alpha"],
        power=params["power"],
        alternative=alternative,
    )
    result = params.copy()
    result[solve_for] = solved
    result["nobs1"] = result["nobs"]
    return result


def _compute_mde(power_obj, nobs1, power, alpha, ratio, alternative):
    """Minimum detectable effect (inverse solve)."""
    return power_obj.solve_power(nobs1=nobs1, power=power, alpha=alpha, ratio=ratio, alternative=alternative)
