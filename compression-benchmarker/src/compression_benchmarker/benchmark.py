import time
from typing import Dict, Any

from .compressors import Compressor


def benchmark_compressor(
    comp: Compressor, data: bytes, runs: int = 3
) -> Dict[str, float]:
    """Benchmark one compressor (avg over `runs`)."""
    if not data:
        raise ValueError("Empty data")

    comp_times_ms: list[float] = []
    decomp_times_ms: list[float] = []
    comp_sizes: list[float] = []

    for _ in range(runs):
        # Compress
        t0 = time.perf_counter()
        cdata = comp.compress(data)
        t1 = time.perf_counter()
        comp_times_ms.append((t1 - t0) * 1000)
        comp_sizes.append(len(cdata))

        # Decompress
        t2 = time.perf_counter()
        _ = comp.decompress(cdata)
        t3 = time.perf_counter()
        decomp_times_ms.append((t3 - t2) * 1000)

    avg_comp_size = sum(comp_sizes) / runs
    avg_comp_ms = sum(comp_times_ms) / runs
    avg_decomp_ms = sum(decomp_times_ms) / runs

    comp_sec = avg_comp_ms / 1000
    decomp_sec = avg_decomp_ms / 1000

    orig_mb = len(data) / 1e6
    comp_mbps = orig_mb / comp_sec if comp_sec > 0 else float("inf")
    decomp_mbps = orig_mb / decomp_sec if decomp_sec > 0 else float("inf")

    size_pct = (1 - avg_comp_size / len(data)) * 100

    return {
        "comp_size": avg_comp_size,
        "size_pct": size_pct,
        "comp_time_ms": avg_comp_ms,
        "decomp_time_ms": avg_decomp_ms,
        "comp_mbps": comp_mbps,
        "decomp_mbps": decomp_mbps,
    }
