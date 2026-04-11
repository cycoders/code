from typing import List, Dict, Any, Tuple
from collections import defaultdict

from .models import Request


def percentile(values: List[float], p: float) -> float:
    """Calculate percentile p (0-100). Simple sorted index impl."""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = int(len(sorted_values) * p / 100.0)
    return sorted_values[index]


def compute_stats(requests: List[Request]) -> Dict[str, Any]:
    """Compute comprehensive load test stats."""
    if not requests:
        return {}

    timestamps = [r.timestamp for r in requests]
    durations = [r.duration for r in requests]
    time_span = max(timestamps) - min(timestamps)
    rps = len(requests) / time_span if time_span > 0 else 0.0

    error_reqs = [r for r in requests if r.status_code >= 400 or r.error]
    error_rate = (len(error_reqs) / len(requests)) * 100

    endpoint_durs = defaultdict(list)
    for r in requests:
        endpoint_durs[r.endpoint].append(r.duration)

    top_endpoints: List[Tuple[str, float, int]] = []
    for endpoint, durs in endpoint_durs.items():
        avg_dur = sum(durs) / len(durs)
        top_endpoints.append((endpoint, avg_dur, len(durs)))
    top_endpoints.sort(key=lambda x: x[1], reverse=True)
    top_endpoints = top_endpoints[:10]

    return {
        "total_requests": len(requests),
        "rps": round(rps, 2),
        "error_rate_pct": round(error_rate, 2),
        "avg_duration_ms": round(sum(durations) / len(durations), 2),
        "p50_ms": round(percentile(durations, 50), 2),
        "p90_ms": round(percentile(durations, 90), 2),
        "p95_ms": round(percentile(durations, 95), 2),
        "p99_ms": round(percentile(durations, 99), 2),
        "time_span_s": round(time_span, 2),
        "top_endpoints": [
            {"endpoint": ep, "avg_ms": round(avg, 2), "count": cnt}
            for ep, avg, cnt in top_endpoints
        ],
    }
