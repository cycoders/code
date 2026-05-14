import asyncio
import logging
from typing import List, Dict, Any

from .clients import fetch_http2, fetch_http3, FetchResult
from .metrics import compute_stats

logger = logging.getLogger(__name__)


async def run_single(url: str, protocol: str, *args, **kwargs) -> FetchResult:
    if protocol == "http3":
        return await fetch_http3(url, *args, **kwargs)
    elif protocol == "http2":
        return await fetch_http2(url, *args, **kwargs)
    raise ValueError(f"Unknown protocol: {protocol}")


async def run_benchmark(
    url: str,
    runs: int,
    http2: bool,
    method: str,
    max_body: int,
    headers: List[str],
    verbose: bool,
) -> Dict[str, List[Dict]]:
    """Run N benchmarks for H3 (+ H2)."""
    logging.basicConfig(level=logging.DEBUG if verbose else logging.WARNING)

    protocols = ["http3"]
    if http2:
        protocols.append("http2")

    h3_results: List[Dict] = []
    h2_results: List[Dict] = []

    for i in range(runs):
        logger.info(f"Run {i+1}/{runs}")
        if "http3" in protocols:
            h3_results.append(asdict(await run_single(url, "http3", method, max_body, headers, verbose)))
        if "http2" in protocols:
            h2_results.append(asdict(await run_single(url, "http2", method, max_body, headers)))
        await asyncio.sleep(0.1)  # Throttle

    return {
        "http3": {
            "raw": h3_results,
            "stats": {
                "connect": compute_stats([r["connect_time"] for r in h3_results]),
                "ttfb": compute_stats([r["ttfb"] for r in h3_results]),
                "total": compute_stats([r["total_time"] for r in h3_results]),
            },
        },
        "http2": {
            "raw": h2_results,
            "stats": {
                "connect": compute_stats([r["connect_time"] for r in h2_results]),
                "ttfb": compute_stats([r["ttfb"] for r in h2_results]),
                "total": compute_stats([r["total_time"] for r in h2_results]),
            },
        } if http2 else None,
        "url": url,
        "runs": runs,
        "config": {"method": method, "max_body": max_body},
    }
