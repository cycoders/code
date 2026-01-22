import sys
from typing import Any, Dict, Optional

import typer
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .measure import BenchmarkResult, MetricName

console = Console()


STATUS_EMOJI = {
    "regression": "🔴",
    "improvement": "🟢",
    "warn": "🟡",
    "pass": "🟢",
}


def delta_pct(current: float, baseline: float) -> float:
    return ((current - baseline) / baseline) * 100 if baseline else 0.0


def status_symbol(delta: float, threshold: float) -> str:
    abs_delta = abs(delta)
    if abs_delta > threshold:
        return "regression" if delta > 0 else "improvement"
    elif abs_delta > threshold / 2:
        return "warn"
    return "pass"


def format_stat(stat: Dict[str, float], unit: str) -> str:
    return f"{stat['mean']:.3f}±{stat['std']:.3f}{unit}"


def report_results(
    current: Optional[BenchmarkResult],
    baseline: Optional[BenchmarkResult],
    threshold: float,
    fail_on_regression: bool = False,
):
    """Print rich table report."""
    if not current:
        typer.echo("No current results.")
        return

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Benchmark", style="cyan")
    table.add_column("Metric", style="green")
    table.add_column("Current", justify="right")
    if baseline:
        table.add_column("Baseline", justify="right")
        table.add_column("Δ%", justify="right")
        table.add_column("Thr", justify="right")
        table.add_column("Status")

    has_regression = False

    for bname, cres in current.items():
        bres = baseline.get(bname) if baseline else None
        for metric in cres:
            cstat = cres[metric]
            units = {
                "wall_time": "s",
                "cpu_time": "s",
                "peak_memory": "MB",
            }
            cfmt = format_stat(cstat, units[metric])

            row = [bname, metric.replace("_", "-"), cfmt]

            if bres:
                bstat = bres[metric]
                delta = delta_pct(cstat["mean"], bstat["mean"])
                bfmt = format_stat(bstat, units[metric])
                status = status_symbol(delta, threshold)
                delta_str = f"{delta:+.1f}%"
                thr_str = f"{threshold:.0f}%"
                row.extend([bfmt, delta_str, thr_str])

                color = {
                    "regression": "red",
                    "improvement": "green",
                    "warn": "yellow",
                    "pass": "green",
                }[status]
                emoji = STATUS_EMOJI[status]
                row.append(f"[{color}]{emoji} {status.upper()}[/{color}]")

                if status == "regression":
                    has_regression = True
            else:
                row.append("[grey]NO BASELINE[/grey]")

            table.add_row(*row)

    console.print(table)

    if baseline and has_regression and fail_on_regression:
        console.print("[bold red]REGRESSIONS DETECTED! Failing CI.[/bold red]")
        sys.exit(1)