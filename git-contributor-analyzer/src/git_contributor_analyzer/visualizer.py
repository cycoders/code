from typing import List
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import ROUNDED

from .types import ContributorStats


def print_table(stats: List[ContributorStats], console: Console) -> None:
    table = Table(title="[bold cyan]Contributor Statistics", box=ROUNDED, show_header=True, header_style="bold magenta")
    table.add_column("Author", style="cyan", no_wrap=True)
    table.add_column("Commits", justify="right")
    table.add_column("Added", justify="right")
    table.add_column("Deleted", justify="right")
    table.add_column("Net LOC", justify="right")
    table.add_column("Active Days", justify="right")
    table.add_column("Max Streak", justify="right")
    table.add_column("Avg Size", justify="right")

    for s in stats[:20]:
        table.add_row(
            f"[bold]{s.name}[/bold] <{s.email}>",
            str(s.commit_count),
            f"{s.total_insertions:,}",
            f"{s.total_deletions:,}",
            f"{s.net_loc:,}",
            str(s.active_days),
            str(s.max_streak),
            str(s.avg_insertions_per_commit),
        )
    console.print(table)

    if stats:
        total_commits = sum(s.commit_count for s in stats)
        total_authors = len(stats)
        top_contributor = stats[0].name
        summary_panel = Panel(
            f"[bold green]Total Contributors:[/bold] {total_authors} | "
            f"[bold green]Total Commits:[/bold] {total_commits:,} | "
            f"[bold green]Top Net Contributor:[/bold] {top_contributor}",
            title="[bold green]Summary",
            border_style="green",
        )
        console.print(summary_panel)


def print_json(stats: List[ContributorStats]) -> None:
    print(json.dumps([s.to_dict() for s in stats], indent=2))
