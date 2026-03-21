import warnings
from dataclasses import dataclass
from typing import Tuple, Any

import numpy as np
from scipy import stats
from scipy.stats import beta
from statsmodels.stats.proportion import (
    proportion_effectsize,
    proportion_confint,
    samplesize_confint_proportion,
)
from statsmodels.stats.power import zt_ind_solve_power, TTestIndPower

@dataclass
class DesignResult:
    n_a: int
    n_b: int
    total: int
    effect_size: float
    warning: str | None = None

@dataclass
class AnalysisResult:
    p_value: float
    ci_a: Tuple[float, float]
    ci_b: Tuple[float, float]
    prob_b_superior: float
    bayes_lift: float
    warning: str | None = None

# Frequentist Design
def design_proportion(
    baseline: float,
    mde: float,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
) -> DesignResult:
    """EvanMiller/StatsModels matching prop power analysis."""
    prop2 = baseline + mde
    if prop2 > 1:
        warnings.warn("MDE pushes prop2 >1, capping")
        prop2 = 1.0
    es = proportion_effectsize(baseline, prop2)
    n_a = zt_ind_solve_power(
        es, alpha=alpha, power=power, ratio=ratio, alternative="two-sided"
    )
    n_a = int(np.ceil(n_a))
    n_b = int(np.ceil(n_a * ratio))
    total = n_a + n_b
    return DesignResult(n_a, n_b, total, es)

def design_mean(
    baseline: float,
    mde: float,
    stddev: float,
    alpha: float = 0.05,
    power: float = 0.8,
    ratio: float = 1.0,
) -> DesignResult:
    """T-test power for means."""
    analysis = TTestIndPower()
    es = mde / stddev  # Cohen's d
    n_a = analysis.solve_power(es, alpha, power, ratio=ratio, alternative="two-sided")
    n_a = int(np.ceil(n_a))
    n_b = int(np.ceil(n_a * ratio))
    total = n_a + n_b
    return DesignResult(n_a, n_b, total, es)

# Frequentist Analysis
def _prop_test_pvalue(a_suc: int, a_tot: int, b_suc: int, b_tot: int, alpha: float) -> float:
    table = [[a_suc, a_tot - a_suc], [b_suc, b_tot - b_suc]]
    if min(table) < 5:
        _, p = stats.fisher_exact(table, alternative="two-sided")
    else:
        _, p, _, _ = stats.chi2_contingency(table, correction=False)
    return p

def _prop_ci(success: int, total: int, alpha: float = 0.05) -> Tuple[float, float]:
    return proportion_confint(success, total, alpha=alpha, method="wilson")

# Bayesian
def bayesian_proportion(
    a_suc: int,
    a_tot: int,
    b_suc: int,
    b_tot: int,
    prior_alpha: float = 1.0,
    prior_beta: float = 1.0,
    mc_samples: int = 100_000,
) -> dict[str, Any]:
    post_a_alpha = a_suc + prior_alpha
    post_a_beta = (a_tot - a_suc) + prior_beta
    post_b_alpha = b_suc + prior_alpha
    post_b_beta = (b_tot - b_suc) + prior_beta

    theta_a = np.random.beta(post_a_alpha, post_a_beta, mc_samples)
    theta_b = np.random.beta(post_b_alpha, post_b_beta, mc_samples)

    prob_b_superior = np.mean(theta_b > theta_a)
    bayes_lift = np.mean((theta_b - theta_a) / theta_a) * 100

    ci_a = np.percentile(theta_a, [2.5, 97.5])
    ci_b = np.percentile(theta_b, [2.5, 97.5])

    return {
        "prob_b_superior": prob_b_superior,
        "bayes_lift": bayes_lift,
        "ci_a": tuple(ci_a),
        "ci_b": tuple(ci_b),
    }

def analyze_proportion(
    a_suc: int,
    a_tot: int,
    b_suc: int,
    b_tot: int,
    alpha: float = 0.05,
    prior_strength: float = 1.0,
    mc_samples: int = 100_000,
) -> AnalysisResult:
    p_value = _prop_test_pvalue(a_suc, a_tot, b_suc, b_tot, alpha)
    ci_a = _prop_ci(a_suc, a_tot, alpha)
    ci_b = _prop_ci(b_suc, b_tot, alpha)

    bayes = bayesian_proportion(a_suc, a_tot, b_suc, b_tot, prior_strength, prior_strength, mc_samples)

    warning = None
    if min(a_suc, b_suc) < 20:
        warning = "Low event counts: prefer Bayes or run longer."
    if p_value > alpha and bayes["prob_b_superior"] > 0.95:
        warning = "Frequentist miss: consider Bayes for direction."

    return AnalysisResult(
        p_value,
        ci_a,
        ci_b,
        bayes["prob_b_superior"],
        bayes["bayes_lift"],
        warning,
    )