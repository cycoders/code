import statistics
from typing import Any, Dict, List

from rich.box import ROUNDED
from rich.console import Console
from rich.table import Table


console = Console()


def percentile(times: List[float], p: float) -> float:
    """Compute percentile."""
    if not times:
        return 0.0
    sorted_times = sorted(times)
    index = int(p * (len(sorted_times) - 1))
    return sorted_times[index]


def make_sparkline(values: List[float], width: int = 30) -> str:
    """Generate sparkline from values."""
    if not values:
        return "▁" * width
    min_v, max_v = min(values), max(values)
    if min_v == max_v:
        return "█" * width
    hist = [0] * width
    for v in values:
        idx = min(int((v - min_v) / (max_v - min_v) * (width - 1)), width - 1)
        hist[idx] += 1
    max_h = max(hist)
    chars = "▁▂▃▄▅▆▇█"
    return "".join(chars[int(h / max_h * (len(chars) - 1))] for h in hist)


def compute_stats(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute statistics from results."""
    success_results = [r for r in results if r["success"]]
    wall_times = [r["wall_time"] for r in success_results]
    cpu_totals = [r["cpu_total"] for r in success_results]
    mem_peaks = [r["mem_peak_mb"] for r in success_results]

    n_total = len(results)
    n_success = len(wall_times)
    n_failed = n_total - n_success

    if n_success == 0:
        return {"error": "All runs failed"}

    return {
        "n_success": n_success,
        "n_failed": n_failed,
        "wall_mean": statistics.mean(wall_times),
        "wall_median": statistics.median(wall_times),
        "wall_std": statistics.stdev(wall_times) if n_success > 1 else 0.0,
        "wall_p95": percentile(wall_times, 0.95),
        "wall_min": min(wall_times),
        "wall_max": max(wall_times),
        "wall_spark": make_sparkline(wall_times),
        "cpu_mean": statistics.mean(cpu_totals),
        "mem_mean": statistics.mean(mem_peaks),
        "mem_max": max(mem_peaks),
    }


def print_results(benchmarked: List[Dict[str, Any]]) -> None:
    """Print rich results table."""
    table = Table(box=ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Runs", justify="right")
    table.add_column("Mean", justify="right")
    table.add_column("±", justify="right")
    table.add_column("Median", justify="right")
    table.add_column("P95", justify="right")
    table.add_column("Min", justify="right")
    table.add_column("Max [sparkline]", justify="right")
    table.add_column("CPU", justify="right")
    table.add_column("Mem (mean/max)", justify="right")

    for item in benchmarked:
        cmd_str = item["command"]
        results = item["results"]
        stats = compute_stats(results)
        if "error" in stats:
            table.add_row(cmd_str, str(len(results)), stats["error"], "", "", "", "", "", "", "")
            continue
        cmd_display = cmd_str[:35] + "..." if len(cmd_str) > 35 else cmd_display
        table.add_row(
            cmd_display,
            f"{stats['n_success']}/{len(results)}",
            f"{stats['wall_mean']*1000:.0f}ms",
            f"{stats['wall_std']*1000:.0f}",
            f"{stats['wall_median']*1000:.0f}ms",
            f"{stats['wall_p95']*1000:.0f}ms",
            f"{stats['wall_min']*1000:.0f}",
            f"{stats['wall_max']*1000:.0f} [{stats['wall_spark']}]",
            f"{stats['cpu_mean']:.2f}s",
            f"{stats['mem_mean']:.1f}/{stats['mem_max']:.1f}MB",
        )
    console.print(table)
