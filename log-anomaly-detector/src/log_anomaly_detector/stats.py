import numpy as np
import pandas as pd
from scipy import stats
from typing import Union


def detect_outliers(
    series: pd.Series,
    method: str = "zscore",
    threshold: float = 3.0,
) -> pd.Series:
    """
    Detect outliers in series using statistical method.

    Returns boolean mask aligned to original index.
    """
    s = series.dropna()
    if len(s) < 3:
        return pd.Series(False, index=series.index)

    if method == "zscore":
        z_scores = np.abs(stats.zscore(s))
        mask = pd.Series(z_scores > threshold, index=s.index)
    elif method == "iqr":
        q1, q3 = s.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        mask = pd.Series(((s < lower) | (s > upper)), index=s.index)
    elif method == "modified_z":
        median = s.median()
        mad = np.median(np.abs(s - median))
        if mad == 0:
            return pd.Series(False, index=series.index)
        mod_z = 0.6745 * (s - median) / mad
        mask = np.abs(mod_z) > threshold
        mask = pd.Series(mask, index=s.index)
    else:
        raise ValueError(f"Unknown method: {method}")

    full_mask = pd.Series(False, index=series.index)
    full_mask.loc[mask.index] = mask
    return full_mask
