from __future__ import annotations
import statistics
from collections import defaultdict, Counter
from typing import List

from rich import console, table
from rich.text import Text

import plotly.express as px
import pandas as pd

from .tree_builder import SpanNode


console = console.Console()


def print_trace_stats(roots: List[SpanNode], title: str = "Trace Statistics"):
    """Print rich stats table."""
    all_nodes = list(_flatten_nodes(roots))
    if not all_nodes:
        return

    durations = [n.span.duration_sec for n in all_nodes]
    services = [n.span.service for n in all_nodes]
    errors = sum(1 for n in all_nodes if n.span.is_error)

    service_stats = _compute_service_stats(all_nodes)

    t = table.Table(title=title, title_style="bold magenta")
    t.add_column("Metric", style="cyan")
    t.add_column("Value", style="green")
    t.add_row("Total Duration", f"{max(n.span.end_time_sec for n in all_nodes):.3f}s")
    t.add_row("Span Count", str(len(all_nodes)))
    t.add_row("Services", str(len(set(services))))
    t.add_row("Error Rate", f"{errors/len(all_nodes)*100:.1f}%" if all_nodes else "0%")
    t.add_row("P95 Latency", f"{statistics.quantiles(durations, n=20)[18]:.3f}s")

    console.print(t)

    # Service table
    s_table = table.Table(title="Service Latencies (P50/P95/P99)", title_style="bold blue")
    s_table.add_column("Service")
    s_table.add_column("Count")
    s_table.add_column("P50")
    s_table.add_column("P95")
    s_table.add_column("P99")
    s_table.add_column("Errors")

    for svc, stats_ in service_stats.items():
        p50 = statistics.median(stats_["durs"])
        p95 = sorted(stats_["durs"])[int(0.95 * len(stats_["durs"]))]
        p99 = sorted(stats_["durs"])[int(0.99 * len(stats_["durs"]))] if len(stats_["durs"]) > 100 else p95
        err_cnt = stats_["errors"]
        s_table.add_row(svc, str(stats_["count"]), f"{p50:.3f}s", f"{p95:.3f}s", f"{p99:.3f}s", str(err_cnt))

    console.print(s_table)


def get_top_bottlenecks(roots: List[SpanNode], top_n: int = 10) -> List[SpanNode]:
    """Return top slowest spans by duration."""
    all_nodes = list(_flatten_nodes(roots))
    return sorted(all_nodes, key=lambda n: n.span.duration_sec, reverse=True)[:top_n]


def print_bottlenecks(roots: List[SpanNode], top_n: int = 10):
    """Print top bottlenecks table."""
    top = get_top_bottlenecks(roots, top_n)
    t = table.Table(title=f"Top {top_n} Bottlenecks", title_style="bold red")
    t.add_column("Operation")
    t.add_column("Duration")
    t.add_column("Self")
    t.add_column("Service")
    t.add_column("Error")

    for node in top:
        error_icon = "[red]❌[/red]" if node.span.is_error else "✅"
        t.add_row(
            node.span.operationName[:30],
            f"{node.span.duration_sec:.3f}s",
            f"{node.self_time:.3f}s",
            node.span.service,
            error_icon,
        )

    console.print(t)


def _compute_service_stats(all_nodes: List[SpanNode]) -> Dict[str, Dict]:
    stats = defaultdict(lambda: {"durs": [], "count": 0, "errors": 0})
    for n in all_nodes:
        svc = n.span.service
        stats[svc]["durs"].append(n.span.duration_sec)
        stats[svc]["count"] += 1
        if n.span.is_error:
            stats[svc]["errors"] += 1
    return dict(stats)


def _flatten_nodes(roots: List[SpanNode]) -> List[SpanNode]:
    for root in roots:
        yield from root.flatten()
