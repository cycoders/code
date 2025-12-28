import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .models import TestCase
from .splitter import Job

console = Console()


def print_summary(tests: list[TestCase], jobs: list[Job]) -> None:
    total = sum(t.duration for t in tests)
    rprint(f"[green]Loaded [bold]{len(tests)}[/bold] tests, total [bold]{total:.1f}s[/bold]")


def print_table(jobs: list[Job]) -> None:
    table = Table(title="[bold cyan]Test Suite Splits[/bold cyan]")
    table.add_column("Job", style="cyan", no_wrap=True)
    table.add_column("Tests", style="magenta")
    table.add_column("Count", justify="right", style="green")
    table.add_column("Total Time", justify="right")

    total_time = sum(j.total_duration for j in jobs)
    avg_time = total_time / len(jobs) if jobs else 0
    max_time = max((j.total_duration for j in jobs), default=0)
    balance = max_time / avg_time if avg_time > 0 else 0

    for job in jobs:
        test_preview = " ".join(str(t) for t in job.tests[:5])
        if len(job.tests) > 5:
            test_preview += " ..."
        table.add_row(
            str(job.index),
            test_preview,
            str(job.count),
            f"{job.total_duration:.1f}s",
        )

    caption = f"Total: [bold]{total_time:.1f}s[/bold] | Balance: [bold]{balance:.2f}x[/bold] (lower=better)"
    table.caption = caption
    console.print(table)


def print_pytest_commands(jobs: list[Job], junit_prefix: str = "split") -> None:
    rprint("\n[bold yellow]Pytest commands:[/bold yellow]")
    for job in jobs:
        k_pattern = "|".join(str(t) for t in job.tests)
        cmd = f"pytest -k \"{k_pattern}\" --junitxml={junit_prefix}-{job.index}.xml"
        rprint(f"[blue]Job {job.index}:[/blue] {cmd}")


def output_json(jobs: list[Job], total_tests: int, total_time: float) -> str:
    data: dict[str, Any] = {
        "meta": {
            "total_tests": total_tests,
            "total_time": total_time,
        },
        "jobs": [
            {
                "index": job.index,
                "tests": [t.id for t in job.tests],
                "test_count": job.count,
                "total_duration": job.total_duration,
            }
            for job in jobs
        ],
    }
    return json.dumps(data, indent=2)