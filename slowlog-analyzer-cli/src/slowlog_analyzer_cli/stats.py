import polars as pl
from typing import Dict, List, Tuple
from .models import SlowQuery
from .fingerprint import fingerprint


def compute_stats(queries: List[SlowQuery], top_n: int = 20) -> Tuple[pl.DataFrame, Dict[str, str]]:
    """Compute aggregated stats and sample queries by fp."""
    if not queries:
        return pl.DataFrame(), {}

    fps = [fingerprint(q.query) for q in queries]
    sample_queries = {}
    for fp, q in zip(fps, queries):
        if fp not in sample_queries:
            sample_queries[fp] = q.query

    df = pl.DataFrame({
        "fp": fps,
        "duration_ms": [q.duration_ms for q in queries],
        "user": [q.user for q in queries],
        "database": [q.database for q in queries],
    })

    aggs = df.group_by("fp").agg([
        pl.count().alias("count"),
        pl.col("duration_ms").mean().round(2).alias("avg_duration_ms"),
        pl.col("duration_ms").sum().alias("total_duration_ms"),
        pl.col("duration_ms").quantile(0.95).alias("p95_ms"),
    ]).sort("total_duration_ms", descending=True).head(top_n)

    return aggs, sample_queries
