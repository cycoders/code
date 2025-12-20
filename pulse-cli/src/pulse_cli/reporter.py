from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from typing import List

from .models import CheckResult

console = Console()


def sparkline(values: List[float], width: int = 40, height: int = 1) -> str:
    """Generate terminal sparkline from values."""
    if not values:
        return " " * width
    mn, mx = min(values), max(values)
    if mn == mx:
        return "─" * width
    norm = [(v - mn) / (mx - mn) for v in values[-width :]]
    chars = " ▁▂▃▄▅▆▇█"
    return "".join(chars[int(n * (len(chars) - 1))] for n in norm)


def render_report(results: List[CheckResult]) -> None:
    """Rich table for latest results."""
    table = Table(title="[bold cyan]Pulse Health Report[/]", box=box.ROUNDED)
    table.add_column("Endpoint", style="cyan", no_wrap=True)
    table.add_column("Status")
    table.add_column("Resp (ms)", justify="right")
    table.add_column("Size KB", justify="right")
    table.add_column("Cert Days", justify="right")
    table.add_column("Success")

    for res in results:
        status = "[green]✅[/green]" if res.success else "[red]❌[/red]"
        time_s = f"{res.response_time_ms:.1f}" if res.response_time_ms else "N/A"
        size_s = f"{res.content_length / 1024:.1f}" if res.content_length else "N/A"
        cert_s = (
            f"[red]{res.cert_expiry_days:.0f}[/red]"
            if res.cert_expiry_days and res.cert_expiry_days < 0
            else f"[yellow]{res.cert_expiry_days:.0f}[/yellow]"
            if res.cert_expiry_days and res.cert_expiry_days < 30
            else f"{res.cert_expiry_days:.0f}" if res.cert_expiry_days
            else "N/A"
        )
        table.add_row(
            res.endpoint_name,
            status,
            time_s,
            size_s,
            cert_s,
            "Yes" if res.success else "No",
        )
    console.print(table)


def render_trend(checks: List[CheckResult], metric: str = "response_time_ms") -> None:
    """Trend table + sparkline."""
    if not checks:
        console.print("[yellow]No history.[/yellow]")
        return
    values = [
        getattr(c, metric) or 0.0 for c in checks if getattr(c, metric) is not None
    ]
    spark = sparkline(values)
    console.print(Panel(spark, title=f"[bold blue]{metric.replace('_', ' ').title()} Trend[/]", box=box.MINIMAL))

    table = Table(title="Recent Checks", box=box.ROUNDED)
    table.add_column("Time")
    table.add_column(metric.replace("_", " ").title())
    table.add_column("Success")
    for c in checks[-10:]:
        val = getattr(c, metric, "N/A")
        table.add_row(c.timestamp.strftime("%H:%M"), f"{val}", "✅" if c.success else "❌")
    console.print(table)