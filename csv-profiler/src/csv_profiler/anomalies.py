from typing import Dict, Any, List
from polars import DataFrame, Expr

ANOMALY_THRESHOLDS = {
    "high_nulls": 20.0,
    "high_cardinality": 90.0,
    "low_cardinality": 1.1,  # almost constant
}


def detect_column_anomalies(col_info: Dict[str, Any], n_rows: int) -> List[str]:
    """Detect issues in a single column."""
    anomalies: List[str] = []
    null_pct = col_info["null_pct"]
    unique_pct = col_info["unique_pct"]
    stats = col_info["stats"]

    if null_pct > ANOMALY_THRESHOLDS["high_nulls"]:
        anomalies.append(f"high_nulls ({null_pct:.1f}%)")

    if unique_pct > ANOMALY_THRESHOLDS["high_cardinality"]:
        anomalies.append("high_cardinality")

    if unique_pct < ANOMALY_THRESHOLDS["low_cardinality"]:
        anomalies.append("constant_value")

    if "std" in stats and stats["std"] == 0:
        anomalies.append("zero_variance")

    # Outliers placeholder (full impl needs Z-score)
    if "std" in stats and stats["std"] > 0:
        mean = stats["mean"]
        std = stats["std"]
        # Simple flag if min/max extreme
        if abs(stats["min"] - mean) > 3 * std or abs(stats["max"] - mean) > 3 * std:
            anomalies.append("potential_outliers")

    return anomalies


def detect_global_anomalies(df: DataFrame, n_rows: int) -> List[str]:
    """Global dataset issues."""
    anoms: List[str] = []
    dupe_pct = 100 - (df.is_duplicated().mean() * 100)
    if dupe_pct < 95:
        anoms.append(f"high_duplicates ({100 - dupe_pct:.1f}% rows duped)")
    return anoms