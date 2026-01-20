from typing import Dict, Any, List, Tuple
from pathlib import Path
import polars as pl
from polars import DataFrame

from csv_profiler.anomalies import detect_column_anomalies, detect_global_anomalies
from csv_profiler.schema_inferrer import infer_schema


def profile_csv(file_path: Path, max_rows: int = 100_000) -> Dict[str, Any]:
    """
    Profile CSV file with streaming Polars.

    Returns structured data for rendering.
    """
    if not file_path.exists():
        raise ValueError(f"File not found: {file_path}")

    # Streaming scan + limit for efficiency
    ldf = pl.scan_csv(
        file_path,
        separator=b",",
        has_header=True,
        infer_schema_length=1000,
        null_values=["", "NULL", "null"],
        ignore_errors=True,
    ).head(max_rows)

    df: DataFrame = ldf.collect(streaming=True)

    n_rows = df.height
    if n_rows == 0:
        return {"error": "Empty file"}

    n_cols = len(df.columns)

    # Global metrics
    dupe_count = df.is_duplicated().sum()
    dupe_pct = (dupe_count / n_rows * 100) if n_rows else 0

    columns: Dict[str, Dict[str, Any]] = {}
    for col_name in df.columns:
        col_series = df[col_name]
        dtype = str(col_series.dtype)
        null_count = col_series.null_count()
        null_pct = (null_count / n_rows * 100) if n_rows else 0
        unique_count = col_series.n_unique()
        unique_pct = (unique_count / n_rows * 100) if n_rows else 0

        top_values: List[Any] | None = None
        if unique_count <= 100:
            top = (
                df.select(pl.col(col_name))
                .value_counts(sort_by="count", descending=True)
                .head(5)
            )
            top_values = top[col_name].to_list()

        stats: Dict[str, Any] = {}
        if col_series.dtype.is_numeric():
            desc = df.select(pl.col(col_name)).describe(
                percentiles=(0.25, 0.5, 0.75)
            )
            stats = {
                k: v
                for k, v in zip(
                    desc.columns[1:],  # skip count
                    desc.row(0, named=False)[1:],
                )
            }

        columns[col_name] = {
            "dtype": dtype,
            "null_count": int(null_count),
            "null_pct": round(null_pct, 2),
            "unique_count": int(unique_count),
            "unique_pct": round(unique_pct, 2),
            "top_values": top_values,
            "stats": stats,
        }

    col_anomalies = {
        col: detect_column_anomalies(col_info, n_rows)
        for col, col_info in columns.items()
    }

    global_anoms = detect_global_anomalies(df, n_rows)

    sch = infer_schema(df)

    return {
        "overview": {
            "rows": n_rows,
            "cols": n_cols,
            "dupe_pct": round(dupe_pct, 2),
        },
        "columns": columns,
        "anomalies": {"columns": col_anomalies, "global": global_anoms},
        "schema": sch,
        "file": str(file_path),
        "max_rows_scanned": min(max_rows, n_rows),
    }