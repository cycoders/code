from typing import List
from datetime import datetime, timedelta
from dataclasses import asdict

import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from cron_simulator.models import Execution


console = Console()


def print_summary(executions: List[Execution], overlaps: List[tuple[datetime, List[str]]]):
    """Print simulation summary table."""
    table = Table(title="[bold cyan]Simulation Summary[/bold cyan]", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    total_execs = len(executions)
    unique_jobs = len({e.job_name for e in executions})
    overlap_count = len(overlaps)

    table.add_row("Total Executions", str(total_execs))
    table.add_row("Unique Jobs", str(unique_jobs))
    table.add_row("Overlap Events", str(overlap_count))

    console.print(table)

    if overlaps:
        console.print("\n[bold red]Overlaps Detected:[/bold red]")
        for ts, jobs in overlaps[:10]:  # Top 10
            console.print(f"  {ts.strftime('%Y-%m-%d %H:%M:%S')}: {', '.join(jobs)}")
        if len(overlaps) > 10:
            console.print(f"  ... and {len(overlaps) - 10} more")


def print_exec_table(executions: List[Execution]):
    """Print detailed executions table."""
    table = Table(title="Executions", box=box.ROUNDED)
    table.add_column("Job", style="cyan")
    table.add_column("Start", style="green")
    table.add_column("End", style="green")
    table.add_column("Duration (s)", style="yellow", justify="right")

    for e in executions:
        duration = (e.end - e.start).total_seconds()
        table.add_row(
            e.job_name,
            e.start.strftime("%Y-%m-%d %H:%M:%S"),
            e.end.strftime("%Y-%m-%d %H:%M:%S"),
            f"{duration:.1f}",
        )

    console.print(table)


def print_gantt(executions: List[Execution], start: datetime, end: datetime, width: int = 100):
    """Print Gantt chart for jobs. Limited to <7 days."""
    duration_td = end - start
    if duration_td > timedelta(days=7):
        console.print("[yellow]Period too long for Gantt (>7d); use --output table[/yellow]")
        return

    jobs = sorted({e.job_name for e in executions})
    gantt_table = Table.grid(expand=True, padding=(0, 1))
    gantt_table.add_column("Job", style="cyan", no_wrap=True)
    gantt_table.add_column("Timeline", ratio=1)

    for job_name in jobs:
        job_execs = [e for e in executions if e.job_name == job_name]
        timeline = get_gantt_timeline(job_execs, start, end, width)
        gantt_table.add_row(job_name, "[▓] Busy | [ ] Idle" + "\n" + timeline)

    console.print(Panel(gantt_table, title="[bold green]Gantt Chart[/bold green]", border_style="blue"))

    scale = f"[dim]{start.strftime('%m-%d %H:%M')} {'─' * (width // 10)} {end.strftime('%H:%M')}[/dim]"
    console.print(Panel(scale, title="Timeline Scale"))


def get_gantt_timeline(execs: List[Execution], start: datetime, end: datetime, width: int = 100) -> str:
    """Generate timeline string for one job."""
    timeline = [" "] * width
    total_secs = (end - start).total_seconds()

    for ex in execs:
        frac_start = (ex.start - start).total_seconds() / total_secs
        frac_end = (ex.end - start).total_seconds() / total_secs
        col_start = max(0, int(frac_start * width))
        col_end = min(width, int(frac_end * width))
        for col in range(col_start, col_end):
            timeline[col] = "▓"

    return "".join(timeline)