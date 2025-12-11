import numpy as np
from typing import List, Dict, Any

def compute_stats(
    latencies: List[float], duration: float, total_requests: int, errors: int
) -> Dict[str, Any]:
    if not latencies:
        return {
            "mean_latency": 0.0,
            "std_latency": 0.0,
            "p50": 0.0,
            "p90": 0.0,
            "p95": 0.0,
            "p99": 0.0,
            "rps": 0.0,
            "error_rate": 1.0,
            "total_requests": total_requests,
            "errors": errors,
        }
    latencies = np.array(latencies)
    return {
        "mean_latency": float(np.mean(latencies)),
        "std_latency": float(np.std(latencies)),
        "p50": float(np.percentile(latencies, 50)),
        "p90": float(np.percentile(latencies, 90)),
        "p95": float(np.percentile(latencies, 95)),
        "p99": float(np.percentile(latencies, 99)),
        "rps": total_requests / duration,
        "error_rate": errors / total_requests if total_requests > 0 else 0.0,
        "total_requests": total_requests,
        "errors": errors,
    }