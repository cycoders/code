from typing import Optional

from rich.console import Console, ConsoleOptions
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.box import Box

from .models import LogSummary


def render_summary(
    summary: LogSummary, console: Optional[Console] = None
) -> None:
    """Render rich summary table."""
    console = console or Console()
    console.print(
        Panel.fit(
            Text(f"Build Log Analysis: {summary.filename}\nParser: {summary.parser_used}", style="bold cyan"),
            box=Box.ROUNDED,
        )
    )

    # Metrics table
    table = Table(title="Summary", box=Box.ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    table.add_row(
        "Total Duration",
        f"{summary.total_duration:.2f}s" if summary.total_duration else "N/A",
    )
    table.add_row("Steps", str(len(summary.steps)))
    table.add_row("Errors", f"[red]{summary.total_errors}[/red]")
    table.add_row("Warnings", f"[yellow]{summary.total_warnings}[/red]")
    console.print(table)

    # Steps table
    if summary.steps:
        steps_table = Table(
            title="Top Steps", box=Box.MINIMAL, show_header=True, header_style="bold blue"
        )
        steps_table.add_column("Name", no_wrap=False)
        steps_table.add_column("Duration", justify="right")
        steps_table.add_column("Status", justify="center")
        steps_table.add_column("Issues", justify="right")
        for step in summary.steps[:20]:
            dur_str = f"{step.duration:.2f}s" if step.duration else "N/A"
            status_style = "green" if step.status == "success" else "red" if "fail" in step.status.lower() else "yellow"
            issues = f"{len(step.errors)}E/{len(step.warnings)}W"
            steps_table.add_row(
                Text(step.name[:40], style="white"),
                Text(dur_str, style="yellow"),
                Text(step.status.upper(), style=status_style),
                Text(issues, style="dim"),
            )
        console.print(steps_table)

    if summary.total_errors > 0:
        console.print("\n[bold red]Sample Errors:[/]" + "\n".join(f"  • {e[:100]}" for s in summary.steps for e in s.errors[:3]))
