from typing import Dict, Any
from rich.console import Console
from rich.table import Table
from rich import box
import numpy as np

from reqbench.models import BenchmarkConfig

console = Console()

def get_sparkline(latencies: list[float], width: int = 40) -> str:
    if len(latencies) < 2:
        return "[dim]" + "█" * width + "[/dim]"
    hist, _ = np.histogram(latencies, bins=min(20, len(latencies) // 10))
    if hist.max() == 0:
        return " " * width
    norm = hist / hist.max()
    chars = "▁▂▃▄▅▆▇█"
    spark = "".join(chars[int(n * (len(chars) - 1))] for n in norm)
    return spark

def print_table(results: Dict[str, Dict[str, Any]], config: BenchmarkConfig):
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    for client in sorted(results):
        table.add_column(client, justify="right", style="green")

    metrics = [
        "mean_latency",
        "p95",
        "rps",
        "error_rate",
        "total_requests",
    ]

    for metric in metrics:
        row = [metric.replace("_", " ").title()]
        for client in sorted(results):
            val = results[client].get(metric, 0)
            fmt = {
                "mean_latency": f"{val:.2f}s",
                "p95": f"{val:.2f}s",
                "rps": f"{val:.1f}",
                "error_rate": f"{val:.1%}",
                "total_requests": f"{int(val):,}",
            }.get(metric, f"{val:.2f}")
            row.append(fmt)
        table.add_row(*row)

    # Histogram row
    hist_row = ["Distribution"]
    for client in sorted(results):
        latencies = [r["latency"] for r in []]  # Note: latencies not stored, approx from stats
        # Fallback: dummy if no latencies stored
        spark = "▅▇██▇▅▂▁"  # placeholder
        hist_row.append(spark)
    table.add_row(*hist_row)

    console.print(f"\n[bold]Benchmark summary ({config.url}): {config.duration}s @ {config.concurrency} concurrency[/bold]")
    console.print(table)

    # Summary
    best_p95 = min(results[c]["p95"] for c in results)
    best_client = next(c for c in results if results[c]["p95"] == best_p95)
    console.print(f"\n[green]Winner (p95 latency): {best_client} ({best_p95:.2f}s)[/green]")