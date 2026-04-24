import csv
import json
from io import StringIO
from typing import Any

import rich.box
from rich.console import Console
from rich.table import Table


def print_results(
    results: list[dict[str, Any]], orig_size: int, fmt: str, console: Console
) -> None:
    """Print benchmark results in table/JSON/CSV."""
    results.sort(key=lambda r: r["size_pct"], reverse=True)

    if fmt == "table":
        table = Table(
            title=f"Compression Benchmarks [{len(results)} configs] ({orig_size/1024**2:.1f} MiB input)",
            box=rich.box.ROUNDED,
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Algo", style="cyan", no_wrap=True)
        table.add_column("Level", justify="right")
        table.add_column("Size %", justify="right")
        table.add_column("Comp Size KiB", justify="right")
        table.add_column("Comp ms", justify="right")
        table.add_column("Decomp ms", justify="right")
        table.add_column("Comp MB/s", justify="right")
        table.add_column("Decomp MB/s", justify="right")

        for r in results:
            size_kib = r["comp_size"] / 1024
            table.add_row(
                r["algo"],
                str(r["level"]),
                f"{r['size_pct']:.1f}%",
                f"{size_kib:.1f}",
                f"{r['comp_time_ms']:.1f}",
                f"{r['decomp_time_ms']:.1f}",
                f"{r['comp_mbps']:.1f}",
                f"{r['decomp_mbps']:.1f}",
            )

        console.print(table)

        if results:
            best_ratio = max(results, key=lambda x: x["size_pct"])
            best_speed = max(results, key=lambda x: x["comp_mbps"])
            console.print(
                f"\n[bold green]🏆 Best ratio:[/bold green] {best_ratio['algo']}-{best_ratio['level']} ({best_ratio['size_pct']:.1f}% ) [bold blue]⚡ Fastest comp:[/bold blue] {best_speed['algo']}-{best_speed['level']} ({best_speed['comp_mbps']:.1f} MB/s)"
            )

    elif fmt == "json":
        out = {
            "orig_size_bytes": orig_size,
            "results": results,
        }
        console.print(json.dumps(out, indent=2))

    elif fmt == "csv":
        fields = [
            "algo",
            "level",
            "size_pct",
            "comp_size",
            "comp_time_ms",
            "decomp_time_ms",
            "comp_mbps",
            "decomp_mbps",
        ]
        sio = StringIO()
        writer = csv.DictWriter(sio, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)
        console.print(sio.getvalue())

    else:
        raise ValueError(f"Unknown output format: {fmt}")
