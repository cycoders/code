import statistics
from typing import List, Dict, Any
from dataclasses import asdict


def compute_stats(values: List[float]) -> Dict[str, float]:
    """Compute mean, stddev, min, max, p95."""
    if not values:
        return {}
    return {
        "mean": statistics.mean(values),
        "stddev": statistics.stdev(values) if len(values) > 1 else 0,
        "min": min(values),
        "max": max(values),
        "p95": sorted(values)[int(0.95 * len(values))],
    }


def compute_throughput(total_time_ms: float, body_size: int) -> float:
    """MB/s."""
    return (body_size / 1024 / 1024) / (total_time_ms / 1000)


def format_ms(value: float, precision: int = 1) -> str:
    return f"{value:.{precision}f}"


def percent_diff(a: float, b: float) -> float:
    return ((a - b) / b) * 100 if b != 0 else 0
