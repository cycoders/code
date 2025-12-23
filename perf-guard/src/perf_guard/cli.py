import hashlib
import sys
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table
from rich import box
from rich.panel import Panel

from perf_guard import __version__
from .benchmark import run_benchmark
from .baseline import load_baseline, save_baseline
from .stats import compute_stats, is_regression, regression_ratio, format_duration, Stats


app = typer.Typer(help=f"Perf Guard v{__version__}")
console = Console()


@app.command()
def baseline(
    command: List[str] = typer.Argument(..., nargs=-1, help="Full command (e.g. 'python script.py arg1')"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Baseline name (default: SHA256(command)[:12])"),
    iterations: int = typer.Option(10, "--iterations", "-i", min=3, help="Benchmark iterations"),
    warmup: int = typer.Option(2, "--warmup", "-w", min=0),
    timeout: float = typer.Option(60.0, "--timeout"),
):
    """Create or update performance baseline. Commit the JSON!"""

    if not command:
        raise typer.BadParameter("Command required")

    cmd_str = " ".join(command)
    if name is None:
        name = hashlib.sha256(cmd_str.encode()).hexdigest()[:12]

    console.print(f"[bold cyan]Creating baseline '{name}'[/] for: [green]{cmd_str}[/]")

    times = run_benchmark(command, iterations, warmup, timeout)
    stats = compute_stats(times)

    save_baseline(name, stats, cmd_str)

    _print_stats_table(stats, title="New Baseline")

    console.print(f"✅ Baseline saved: [bold].perfguard-baselines/{name}.json[/]")
    console.print("💡 [italic]Commit this file to git for CI checks![/]")


@app.command()
def check(
    command: List[str] = typer.Argument(..., nargs=-1, help="Full command"),
    name: Optional[str] = typer.Option(None, "--name", "-n"),
    iterations: int = typer.Option(10, "--iterations", "-i", min=3),
    warmup: int = typer.Option(2, "--warmup", "-w"),
    threshold: float = typer.Option(0.1, "--threshold", "-t", help="Regression threshold (default 10%)"),
    timeout: float = typer.Option(60.0, "--timeout"),
):
    """Check against baseline. Exits 1 on regression."""

    if not command:
        raise typer.BadParameter("Command required")

    cmd_str = " ".join(command)
    if name is None:
        name = hashlib.sha256(cmd_str.encode()).hexdigest()[:12]

    old_stats = load_baseline(name)
    if old_stats is None:
        raise typer.Exit(f"❌ No baseline '{name}'. Run: perf-guard baseline {cmd_str}", code=2)

    console.print(f"[bold cyan]Checking '{name}'[/]: [green]{cmd_str}[/]")

    times = run_benchmark(command, iterations, warmup, timeout)
    new_stats = compute_stats(times)

    ratio = regression_ratio(old_stats, new_stats)
    regressed = is_regression(old_stats, new_stats, threshold)

    _print_comparison_table(old_stats, new_stats, ratio)

    status = "🚨 REGRESSED" if regressed else "✅ PASSED"
    style = "red" if regressed else "green"
    console.print(Panel(f"[bold]{status}[/bold] ({ratio*100:+.1f}%)", style=style))

    if regressed:
        raise typer.Exit(1)


@app.version(__version__)
@app.command()
def version():
    console.print(f"Perf Guard {__version__}")


def _print_stats_table(stats: Stats, title: str) -> None:
    table = Table(title=title, box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value")

    table.add_row("Mean", format_duration(stats["mean"]))
    stdev_str = f"{stats['stdev']:.3f}s" if stats["stdev"] > 0 else "N/A"
    table.add_row("Std Dev", stdev_str)
    table.add_row("Min", format_duration(stats["min"]))
    table.add_row("Max", format_duration(stats["max"]))
    table.add_row("Iterations", str(stats["iterations"]))

    console.print(table)


def _print_comparison_table(old: Stats, new: Stats, ratio: float) -> None:
    table = Table(title="Performance Comparison", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Baseline", style="green")
    table.add_column("Current", style="magenta")
    table.add_column("Change", style="yellow")

    table.add_row("Mean", format_duration(old["mean"]), format_duration(new["mean"]), f"{ratio*100:+.1f}%")
    table.add_row(
        "Std Dev",
        f"{old['stdev']:.3f}s",
        f"{new['stdev']:.3f}s",
        "",
    )
    table.add_row("Min", format_duration(old["min"]), format_duration(new["min"]), "")
    table.add_row("Max", format_duration(old["max"]), format_duration(new["max"]), "")
    table.add_row("Iterations", str(old["iterations"]), str(new["iterations"]), "")

    console.print(table)