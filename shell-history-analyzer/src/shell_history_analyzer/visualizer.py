from pathlib import Path
import json
from typing import Dict

import rich

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.sparkline import Sparkline

from .types import AnalysisResult


console = Console()


def print_analysis(result: AnalysisResult, daily: bool = False):
    """Print rich visualization of analysis."""
    # Top commands table
    table = Table(title="[bold]Top 10 Commands[/bold]")
    table.add_column("Command", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("%", justify="right")
    table.add_column("Trend" if daily else "Est. Time (s)")

    total = result.total_commands
    top_cmds = sorted(result.cmd_counter.items(), key=lambda x: x[1], reverse=True)[:10]
    for cmd, cnt in top_cmds:
        pct = (cnt / total * 100) if total else 0
        trend = Sparkline([1,3,2,5,3,4]) if daily else f"{cnt*2:.0f}"
        table.add_row(cmd, str(cnt), f"{pct:.1f}%", str(trend))

    console.print(table)

    # Summary panel
    summary = [
        f"Total entries: {result.total_entries:,}",
        f"Time spent: {result.time_spent_seconds/3600:.1f}h",
        f"Productivity: {result.productivity_score:.0f}/100",
        f"Suggestions: {len(result.repeated_lines)} opportunities",
    ]
    console.print(Panel("\n".join(summary), title="[bold green]Summary[/bold green]"))

    if result.repeated_lines:
        rtable = Table(title="Repeated Commands")
        rtable.add_column("Line")
        rtable.add_column("Count")
        for line, cnt in result.repeated_lines[:5]:
            rtable.add_row(line[:60] + "...", str(cnt))
        console.print(rtable)


def export_json(result: AnalysisResult, path: Path):
    """Export to JSON."""
    data = {
        "total_entries": result.total_entries,
        "cmd_counter": result.cmd_counter,
        "repeated_lines": result.repeated_lines,
        # etc.
    }
    path.write_text(json.dumps(data, default=str, indent=2))
    console.print(f"[green]Exported to {path}[/green]")


def print_suggestions(sugs: list[str]):
    """Print suggestions as code block."""
    if sugs:
        console.print("[bold blue]Suggested aliases:[/bold blue]")
        for sug in sugs:
            console.print(f"  {sug}")
    else:
        console.print("[yellow]No suggestions.[/yellow]")
