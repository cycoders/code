from rich.console import Console, ConsoleOptions
from rich.table import Table
from rich import box
from typing import List

from .benchmark import Result


def print_results(console: Console, results: List[Result]) -> None:
    """Print rich benchmark table + summary."""

    table = Table(
        title="[bold cyan]SerDes Benchmark Results[/]",
        box=box.ROUNDED,
        title_style="bold magenta",
        show_header=True,
        header_style="bold white",
    )

    table.add_column("Format", style="cyan", no_wrap=True)
    table.add_column("Size KB", justify="right")
    table.add_column("Ser ms", justify="right")
    table.add_column("Deser ms", justify="right")
    table.add_column("Total ms", justify="right")
    table.add_column("ops/s", justify="right")
    table.add_column("OK", justify="center")
    table.add_column("Ser ±", justify="right")

    # Sort by total time per KB (efficiency)
    eff_results = sorted(results, key=lambda r: r.total_time_ms / max(r.size_kb, 0.001))

    for r in eff_results:
        fidelity = "✅" if r.fidelity else "❌"
        table.add_row(
            r.format_name,
            f"{r.size_kb:.1f}",
            f"{r.ser_time_ms:.3f}",
            f"{r.deser_time_ms:.3f}",
            f"{r.total_time_ms:.3f}",
            f"{r.throughput:,.0f}",
            fidelity,
            f"{r.ser_stdev_ms:.3f}",
        )

    console.print(table)

    if results:
        best = min(results, key=lambda r: r.total_time_ms)
        console.print(
            f"\n[bold green]🏆 Best overall: {best.format_name} [/]({best.total_time_ms:.3f}ms total, {best.size_kb:.1f}KB)"
        )
        smallest = min(results, key=lambda r: r.size_kb)
        console.print(
            f"[bold blue]📦 Smallest: {smallest.format_name} [/]({smallest.size_kb:.1f}KB)"
        )
