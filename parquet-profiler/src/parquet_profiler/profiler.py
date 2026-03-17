import pyarrow.dataset as ds
from typing import List
from tqdm import tqdm
from .stats import compute_stats
from .schema import get_schema
from .types import ProfileResult, CompareResult, ColumnStats

def profile_dataset(path: str, columns: List[str] = None, limit_samples: int = 1000) -> ProfileResult:
    dataset = ds.dataset(path)
    schema = get_schema(path)

    if columns is None:
        columns = [f.name for f in schema.fields]

    col_stats = []
    alerts = []
    for col in tqdm(columns, desc="Computing stats"):
        if col in [f["name"] for f in schema.fields]:
            stats = compute_stats(dataset, col, limit_samples)
            col_stats.append(stats)
            alerts.extend(stats.quality_alerts)

    return ProfileResult(path=path, schema=schema, columns=col_stats, alerts=list(set(alerts)))

def compare_datasets(path1: str, path2: str) -> CompareResult:
    schema1 = get_schema(path1)
    schema2 = get_schema(path2)

    schema_diff = {}
    if schema1.num_columns != schema2.num_columns:
        schema_diff["num_columns"] = f"{schema1.num_columns} vs {schema2.num_columns}"
    # More diffs...

    stats_diffs = []  # Implement full diff logic
    return CompareResult(path1=path1, path2=path2, schema_diff=schema_diff, stats_diffs=stats_diffs)
