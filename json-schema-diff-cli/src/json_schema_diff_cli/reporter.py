from typing import List, Optional

import rich

from rich.console import Console
from rich.table import Table
from rich.box import ROUNDED

from .diff_model import DiffIssue
from .compatibility import BREAKING_TYPES


def report_diffs(
    issues: List[DiffIssue],
    console: Optional[Console] = None,
    show_breaking_only: bool = False,
) -> None:
    """Render rich table of issues."""

    if console is None:
        console = Console()

    if not issues:
        console.print("[green bold]✅ No differences detected[/green bold]")
        return

    table = Table(title="Schema Diff Report", box=ROUNDED, show_header=True)
    table.add_column("Path", style="cyan", no_wrap=True)
    table.add_column("Type", style="magenta")
    table.add_column("Description")
    table.add_column("Old", style="dim")
    table.add_column("New", style="dim")

    filtered = issues
    if show_breaking_only:
        filtered = [i for i in issues if i.issue_type in BREAKING_TYPES]

    for issue in filtered:
        row_style = "red" if issue.issue_type in BREAKING_TYPES else "yellow"
        old_str = (
            str(issue.old_value)[:50] + "..."
            if issue.old_value and len(str(issue.old_value)) > 50
            else str(issue.old_value or "")
        )
        new_str = (
            str(issue.new_value)[:50] + "..."
            if issue.new_value and len(str(issue.new_value)) > 50
            else str(issue.new_value or "")
        )
        table.add_row(
            issue.path,
            issue.issue_type.replace("_", " ").title(),
            issue.description,
            old_str,
            new_str,
            style=row_style,
        )

    console.print(table)

    if show_breaking_only and len(filtered) < len(issues):
        console.print(f"[dim]... {len(issues) - len(filtered)} non-breaking issues[/dim]")

    summary = f"[bold]{len([i for i in issues if i.issue_type in BREAKING_TYPES])} breaking / {len(issues)} total"
    console.print(f"\n{summary}")