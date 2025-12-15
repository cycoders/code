from typing import List

import rich.console
import rich.table

from .issue import Issue


console = rich.console.Console()


def report(issues: List[Issue]) -> None:
    """Print rich table report of issues."""

    if not issues:
        return

    table = rich.table.Table(title="[bold red]Deadcode Report[/]")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Line", justify="right", style="green")
    table.add_column("Name", style="magenta")
    table.add_column("Type", style="yellow")
    table.add_column("Confidence", justify="right")
    table.add_column("Description")

    # Sort: high conf first, then file, line
    sorted_issues = sorted(
        issues, key=lambda i: (-i.confidence, i.file_path, i.line_no)
    )

    for issue in sorted_issues:
        table.add_row(
            issue.file_path,
            str(issue.line_no),
            issue.name,
            issue.issue_type.replace("unused_", ""),
            f"{issue.confidence}%",
            issue.description,
        )

    console.print(table)

    summary = f"\n[bold]Total issues: {len(issues)} ([red]{len([i for i in issues if i.confidence >= 90])} high[/], "
    summary += f"[yellow]{len([i for i in issues if 70 <= i.confidence < 90])} med[/], "
    summary += f"[green]{len([i for i in issues if i.confidence < 70])} low)[/bold]"
    console.print(summary)
