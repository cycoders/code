from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse
import statistics

SLOW_THRESHOLD = 2000  # ms
LARGE_THRESHOLD = 1024 * 1024  # 1MB


def compute_stats(entries: List[Dict]) -> Dict[str, float]:
    """Compute high-level stats."""
    times = [e.get("time", 0) for e in entries]
    sizes = [e.get("response", {}).get("bodySize", 0) for e in entries]
    errors = [e for e in entries if e.get("response", {}).get("status", 0) >= 400]

    total_req = len(entries)
    return {
        "total_requests": total_req,
        "avg_response_time": statistics.mean(times) if times else 0,
        "p95_time": statistics.quantiles(times, n=20, method="inclusive")[-1]
        if len(times) >= 20
        else (max(times) if times else 0),
        "total_transfer_size_kb": sum(sizes) / 1024,
        "error_rate_pct": (len(errors) / total_req * 100) if total_req else 0,
    }


def top_slow(entries: List[Dict], n: int = 10) -> List[Dict]:
    """Top N slowest requests."""
    return sorted(
        [e for e in entries if e.get("time")],
        key=lambda e: e["time"],
        reverse=True,
    )[:n]


def domains(entries: List[Dict]) -> Counter:
    """Domain request counts."""
    return Counter(
        urlparse(e.get("request", {}).get("url", "")).netloc
        for e in entries
        if e.get("request", {}).get("url")
    )


def resource_types(entries: List[Dict]) -> Counter:
    """MIME type breakdowns."""
    return Counter(
        e.get("response", {}).get("content", {}).get("mimeType", "unknown")
        for e in entries
        if e.get("response", {}).get("content")
    )


def detect_anomalies(entries: List[Dict]) -> List[str]:
    """Detect common perf issues."""
    anomalies = []
    for e in entries:
        time = e.get("time", 0)
        size = e.get("response", {}).get("bodySize", 0)
        status = e.get("response", {}).get("status", 0)
        if time > SLOW_THRESHOLD:
            anomalies.append(f"Slow request: {e.get('request', {}).get('url', '')[:100]} ({time}ms)")
        if size > LARGE_THRESHOLD:
            anomalies.append(f"Large payload: {e.get('request', {}).get('url', '')[:100]} ({size/1024/1024:.1f}MB)")
        if status >= 400:
            anomalies.append(f"Error {status}: {e.get('request', {}).get('url', '')[:100]}")
    return list({a: None for a in anomalies}.keys())[:20]  # Dedupe top 20