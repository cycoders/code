import statistics
from typing import List

from .types import Stats, Times


def compute_stats(times: Times) -> Stats:
    times = [t for t in times if t > 0]
    if not times:
        raise ValueError("No valid run times recorded")

    n = len(times)
    mean = statistics.mean(times)
    stdev = statistics.stdev(times) if n > 1 else 0.0

    return {
        "mean": mean,
        "stdev": stdev,
        "min": min(times),
        "max": max(times),
        "iterations": n,
        "unit": "s",
    }


def is_regression(old_stats: Stats, new_stats: Stats, threshold: float) -> bool:
    return new_stats["mean"] > old_stats["mean"] * (1 + threshold)


def regression_ratio(old_stats: Stats, new_stats: Stats) -> float:
    return (new_stats["mean"] / old_stats["mean"]) - 1


def format_duration(seconds: float, precision: int = 3) -> str:
    if seconds == 0:
        return "0s"
    elif seconds < 0.001:
        return f"{seconds * 1_000_000:.{precision}f}μs"
    elif seconds < 1:
        return f"{seconds * 1000:.{precision}f}ms"
    else:
        return f"{seconds:.{precision}f}s"