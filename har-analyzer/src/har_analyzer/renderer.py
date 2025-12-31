from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text
from collections import Counter
from typing import Dict, List, Any

console = Console()


def render_stats(stats: Dict[str, float]):
    table = Table(title="📊 Overview Stats", box=box.ROUNDED, expand=True)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Total Requests", f"{stats['total_requests']:,}")
    table.add_row("Avg Response Time", f"{stats['avg_response_time']:.0f}ms")
    table.add_row("P95 Response Time", f"{stats['p95_time']:.0f}ms")
    table.add_row("Total Transfer Size", f"{stats['total_transfer_size_kb']:.1f}KB")
    table.add_row(
        "Error Rate",
        f"{stats['error_rate_pct']:.1f}%" + (" [red]⚠️[/red]" if stats['error_rate_pct'] > 1 else ""),
    )
    console.print(table)


def render_waterfall(entries: List[Dict]):
    table = Table(
        title="🌊 Waterfall (Top Slowest)", box=box.MINIMAL_DOUBLE_HEAD, expand=True
    )
    table.add_column("Method", style="cyan", no_wrap=True)
    table.add_column("URL", style="white")
    table.add_column("Status", style="green")
    table.add_column("Time", justify="right", style="yellow")
    table.add_column("Size", justify="right")
    table.add_column("Wait", justify="right")
    table.add_column("Recv", justify="right")
    for e in entries:
        req = e.get("request", {})
        resp = e.get("response", {})
        timings = e.get("timings", {})
        url_short = (
            req.get("url", "")[:70].rpartition("/")[-1]
            if "/" in req.get("url", "")
            else req.get("url", "")[:70]
        ) + "..." if len(req.get("url", "")) > 70 else req.get("url", "")
        status = resp.get("status", "-")
        status_style = "red" if status >= 400 else "green" if status < 300 else "yellow"
        size_kb = resp.get("bodySize", 0) / 1024
        table.add_row(
            req.get("method", "GET"),
            Text(url_short),
            Text(str(status), style=status_style),
            f"{e.get('time', 0):.0f}ms",
            f"{size_kb:.0f}KB",
            f"{timings.get('wait', 0):.0f}ms",
            f"{timings.get('receive', 0):.0f}ms",
        )
    console.print(table)


def render_domains(counter: Counter):
    if not counter:
        return
    table = Table(title="🌐 Domains", box=box.ROUNDED)
    table.add_column("Domain", style="blue")
    table.add_column("Requests", justify="right")
    table.add_column("%", justify="right")
    total = sum(counter.values())
    for dom, count in counter.most_common(10):
        pct = count / total * 100
        table.add_row(dom, str(count), f"{pct:.1f}%")
    console.print(table)


def render_types(counter: Counter):
    if not counter:
        return
    table = Table(title="📦 Resource Types", box=box.ROUNDED)
    table.add_column("MIME Type", style="green")
    table.add_column("Count", justify="right")
    table.add_column("%", justify="right")
    total = sum(counter.values())
    for mime, count in counter.most_common():
        pct = count / total * 100
        table.add_row(mime, str(count), f"{pct:.1f}%")
    console.print(table)


def render_anomalies(anomalies: List[str]):
    panel = Panel(
        "\n".join(f"• {a}" for a in anomalies),
        title="⚠️  Anomalies",
        border_style="red",
    )
    console.print(panel)