import matplotlib.pyplot as plt
import numpy as np
from typing import Optional

from .power_analysis import TTestIndPower, TTestPower, NormalIndPower, FTestAnovaPower


def power_curve_plot(
    test_type: str,
    effect_size: float,
    alpha: float,
    ratio: float,
    alternative: str,
    x_vs: str,
    output_path: str,
):
    """Plot power curve (power vs nobs or effect_size)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(f"Power Curve: {test_type.title()} (effect={effect_size:.2f}, α={alpha})")
    ax.grid(True, alpha=0.3)
    ax.set_xlabel(x_vs.replace('_', ' ').title())
    ax.set_ylabel("Power")

    if test_type == "ttest-ind":
        power_obj = TTestIndPower()
    elif test_type == "ttest-paired":
        power_obj = TTestPower()
        ratio = 1.0  # ignored
    elif test_type == "prop-ztest":
        power_obj = NormalIndPower()
    else:
        power_obj = FTestAnovaPower()

    if x_vs == "nobs":
        x = np.logspace(np.log10(10), np.log10(10000), 100)
        y = np.array([power_obj.power(effect_size, n, alpha, ratio, alternative) for n in x])
        target_line = 0.8
        ax.axhline(target_line, color="r", linestyle="--", label=f"Target Power = {target_line}")
    else:  # effect_size
        x = np.linspace(0.01, 1.5, 100)
        y = np.array([power_obj.power(es, 500, alpha, ratio, alternative) for es in x])  # fixed n=500
        ax.axvline(effect_size, color="g", linestyle="--", label="Given Effect")

    ax.plot(x, y, linewidth=2)
    ax.set_ylim(0, 1)
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
