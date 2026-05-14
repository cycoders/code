import json
import csv
from io import StringIO
from typing import Dict, Any

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.progress import *

import statistics

from .metrics import compute_throughput, format_ms, percent_diff

console = Console()


def print_results(results: Dict[str, Any], fmt: str) -> None:
    if fmt == "json":
        print(json.dumps(results, indent=2))
        return
    if fmt == "csv":
        print_csv(results)
        return

    # table
    print_table(results)


def print_table(results: Dict[str, Any]) -> None:
    h3_stats = results["http3"]["stats"]
    h2_stats = results["http2"]["stats"] if results["http2"] else None

    table = Table(title="HTTP/3 vs HTTP/2 Benchmark", show_header=True, box=Table.BOX_HEAVY_BORDER)
    table.add_column("Protocol", style="cyan")
    table.add_column("Conn (ms)", justify="right")
    table.add_column("TTFB (ms)", justify="right")
    table.add_column("Total (ms)", justify="right")
    table.add_column("Thput (MB/s)", justify="right")

    def add_row(proto: str, stats: Dict[str, Dict]):
        conn = format_ms(stats["connect"]["p95"]) + f" ±{format_ms(stats['connect']['stddev'])}"
        ttfb = format_ms(stats["ttfb"]["p95"]) + f" ±{format_ms(stats['ttfb']['stddev'])}"
        total = format_ms(stats["total"]["p95"]) + f" ±{format_ms(stats['total']['stddev'])}"
        # sparkline placeholder
        spark = "▁▂▅▆█"[:int(stats["total"]["mean"] / 10) % 5 + 1]
        thput = f"{compute_throughput(stats['total']['mean'], 1024*100):.2f}"
        table.add_row(proto, conn, ttfb, total, thput + f" {spark}")

    add_row("HTTP/3 (QUIC)", h3_stats)
    if h2_stats:
        add_row("HTTP/2", h2_stats)
        h3_mean_total = h3_stats["total"]["mean"]
        h2_mean_total = h2_stats["total"]["mean"]
        gain = percent_diff(h2_mean_total, h3_mean_total)
        table.add_row(
            Text("H3 Gain", style="green"),
            f"{gain:.0f}% faster conn" if gain > 0 else "",
            f"{gain:.0f}% lower TTFB" if gain > 0 else "",
            f"{gain:.0f}% faster total" if gain > 0 else "",
            f"{(gain+100):.0f}% higher thput" if gain > 0 else "",
        )

    console.print(table)

    console.print(f"\n[green]HTTP/3 supported: ✅ (runs: {results['runs']}, method: {results['config']['method']})[/green]")


def print_csv(results: Dict[str, Any]) -> None:
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["protocol", "metric", "mean", "p95", "stddev"])
    writer.writeheader()
    for proto, data in [("http3", results["http3"]), ("http2", results["http2"])]:
        if data:
            for metric in ["connect", "ttfb", "total"]:
                stats = data["stats"][metric]
                writer.writerow({
                    "protocol": proto,
                    "metric": metric,
                    "mean": stats["mean"],
                    "p95": stats["p95"],
                    "stddev": stats["stddev"],
                })
    print(output.getvalue())
