from typing import List, Dict, Any, Set
from polars import DataFrame, Expr, col, lit, when, concat_str, int_range


def compute_key_hash(df: DataFrame, keys: List[str]) -> DataFrame:
    """
    Add key_hash column: concat(keys, '|') or row index if no keys.
    """
    if keys:
        # Escape '|' in keys to avoid collision
        key_exprs = [
            col(k).cast(str).str.replace_all("\|\\+", "_PIPE_").str.replace_all("\\n", "_NL_")
            for k in keys
        ]
        df = df.with_columns(concat_str(key_exprs, separator="|").alias("key_hash"))
    else:
        df = df.with_columns(int_range(0, lit(df.height)).alias("key_hash"))
    return df


def detect_changes(merged: DataFrame, data_cols: Set[str], tol: float) -> List[Dict[str, Any]]:
    """
    Detect changed cells in matched rows.
    """
    changes: List[Dict[str, Any]] = []
    match_mask = col("key_hash_right").is_not_null()

    for col_name in data_cols:
        col_right = f"{col_name}_right"
        if col_right not in merged.columns:
            continue

        # Null diff
        null_left = col(col_name).is_null()
        null_right = col(col_right).is_null()
        mask_null_diff = null_left != null_right

        # Value diff
        dtype_left = merged[col_name].dtype
        if dtype_left in [float, "f64", "f32"]:
            abs_diff = (col(col_name) - col(col_right)).abs()
            mask_val_diff = abs_diff > tol
        else:
            mask_val_diff = col(col_name) != col(col_right)

        change_mask = match_mask & (mask_null_diff | mask_val_diff)

        changed_df = merged.filter(change_mask).select([
            "row_idx",
            "key_hash",
            col_name,
            col_right,
        ])

        for row in changed_df.iter_rows(named=True):
            changes.append({
                "row_idx_left": row["row_idx"],
                "key": row["key_hash"],
                "col": col_name,
                "old": row[col_name],
                "new": row[col_right],
            })

    return changes