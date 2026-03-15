import pandas as pd
import sys

from .config import AnomalyConfig

from .stats import detect_outliers


def find_anomalies(df: pd.DataFrame, config: AnomalyConfig) -> pd.DataFrame:
    """
    Detect anomalies across fields, optionally grouped.

    Adds 'is_anomaly' column.
    """
    if df.empty:
        return df

    is_anomaly = pd.Series(False, index=df.index)

    for field in config.fields:
        if field not in df.columns:
            print(f"[WARN] Field '{field}' missing, skipping", file=sys.stderr)
            continue
        field_outliers = detect_outliers(df[field], config.method, config.threshold)
        is_anomaly |= field_outliers

    if config.group_by:
        for group_cols in config.group_by:
            for name, group in df.groupby(group_cols):
                group_is_anomaly = pd.Series(False, index=group.index)
                for field in config.fields:
                    if field in group.columns:
                        field_mask = detect_outliers(
                            group[field], config.method, config.threshold
                        )
                        group_is_anomaly |= field_mask
                # Map back
                temp_mask = pd.Series(False, index=df.index)
                temp_mask.loc[group.index] = group_is_anomaly
                is_anomaly |= temp_mask

    df["is_anomaly"] = is_anomaly
    return df[df["is_anomaly"]].copy()
