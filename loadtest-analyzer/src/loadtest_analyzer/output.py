from typing import Dict, Any

from rich.console import Console, RenderableType
from rich.table import Table
from rich.panel import Panel


def print_stats(console: Console, stats: Dict[str, Any]) -> None:
    """Print stats in rich table."""
    table = Table(title="[bold cyan]Load Test Analysis[/bold cyan]", expand=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Total Requests", str(stats["total_requests"]))
    table.add_row("RPS", f"{stats['rps']}")
    table.add_row("Error Rate", f"{stats['error_rate_pct']}%")
    table.add_row("Avg Duration", f"{stats['avg_duration_ms']}ms")
    table.add_row("P50", f"{stats['p50_ms']}ms")
    table.add_row("P90", f"{stats['p90_ms']}ms")
    table.add_row("P95", f"{stats['p95_ms']}ms")
    table.add_row("P99", f"{stats['p99_ms']}ms")
    table.add_row("Time Span", f"{stats['time_span_s']}s")

    console.print(table)

    # Top endpoints
    if stats.get("top_endpoints"):
        etable = Table(title="[bold yellow]Top 10 Slowest Endpoints[/bold yellow]", expand=True)
        etable.add_column("Endpoint")
        etable.add_column("Avg (ms)")
        etable.add_column("Count")
        for ep_stats in stats["top_endpoints"]:
            etable.add_row(
                ep_stats["endpoint"],
                f"{ep_stats['avg_ms']}",
                str(ep_stats["count"]),
            )
        console.print(etable)


def print_compare(console: Console, stats1: Dict[str, Any], stats2: Dict[str, Any], label1: str = "Baseline", label2: str = "Current") -> None:
    """Print side-by-side comparison with regression highlights."""
    def color_delta(v1: float, v2: float) -> str:
        if v2 > v1 * 1.1:
            return f"[bold red]{v2:.2f}[/bold red] ↑{((v2/v1-1)*100):+.1f}%"
        elif v2 < v1 * 0.9:
            return f"[bold green]{v2:.2f}[/bold green] ↓{((v1/v2-1)*100):+.1f}%"
        else:
            return f"{v2:.2f}"

    ctable = Table.grid(expand=True)
    ctable.add_column(label1, justify="right")
    ctable.add_column(label2, justify="right")

    metrics = ["avg_duration_ms", "p90_ms", "p95_ms", "p99_ms", "error_rate_pct"]
    for m in metrics:
        v1 = stats1.get(m, 0)
        v2 = stats2.get(m, 0)
        ctable.add_row(str(v1), color_delta(v1, v2))

    left_panel = Panel.fit(ctable, title=f"[bold blue]{label1} vs {label2}[/bold blue]")
    console.print(left_panel)
