from pathlib import Path
from typing import List, Set, Dict, Any
import polars as pl
from rich.progress import Progress, SpinnerColumn, TextColumn
from .schema import compare_schemas
from .diff_engine import compute_key_hash, detect_changes


def diff_csvs(
    file1: str,
    file2: str,
    keys: List[str],
    ignore: List[str],
    tol: float,
) -> Dict[str, Any]:
    """
    Core diff logic: schema + data diffs.

    Returns serializable dict for rendering/JSON.
    """
    ignore_set: Set[str] = set(ignore)

    # Read with progress
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task1 = progress.add_task("[cyan]Reading left CSV...", total=None)
        df1 = pl.scan_csv(file1, infer_schema_length=50000).collect()
        progress.remove_task(task1)

        task2 = progress.add_task("[cyan]Reading right CSV...", total=None)
        df2 = pl.scan_csv(file2, infer_schema_length=50000).collect()
        progress.remove_task(task2)

    # Schema diff
    schema_diff = compare_schemas(df1, df2, ignore_set)

    # Drop ignored columns
    df1_dropped = df1.drop([c for c in ignore if c in df1.columns])
    df2_dropped = df2.drop([c for c in ignore if c in df2.columns])

    # Add indices and keys
    df1_idx = df1_dropped.with_row_index("row_idx")
    df2_idx = df2_dropped.with_row_index("row_idx")

    df1_keyed = compute_key_hash(df1_idx, keys)
    df2_keyed = compute_key_hash(df2_idx, keys)

    # Full outer join
    merged = df1_keyed.join(df2_keyed, on="key_hash", how="full", suffix="_right")

    # Stats
    stats = {
        "rows_left": df1_keyed.height,
        "rows_right": df2_keyed.height,
        "matches": merged.filter(pl.col("key_hash_right").is_not_null()).height,
        "only_left": merged.filter(pl.col("key_hash_right").is_null()).height,
        "only_right": merged.filter(pl.col("key_hash").is_null()).height,
    }

    # Data cols (exclude index/hash)
    data_cols = set(df1_keyed.columns) & set(df2_keyed.columns) - {"row_idx", "key_hash"}

    # Cell changes
    cell_changes = detect_changes(merged, data_cols, tol)

    # Added/removed as dicts
    only_left_df = (
        merged.filter(pl.col("key_hash_right").is_null())
        .select([c for c in df1_keyed.columns if not c.endswith("_right")])
        .to_dicts()
    )
    only_right_df = (
        merged.filter(pl.col("key_hash").is_null())
        .select([c for c in df2_keyed.columns if not c.startswith("row_idx") and c != "key_hash"])
        .to_dicts()
    )

    return {
        "schema_diff": schema_diff,
        "stats": {k: int(v) for k, v in stats.items()},
        "added_rows": only_right_df,
        "removed_rows": only_left_df,
        "cell_changes": cell_changes,
    }