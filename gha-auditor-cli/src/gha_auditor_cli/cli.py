import json
import sys
from pathlib import Path
from typing import List

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .auditor import audit_directory
from .issue import Issue, Severity


app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def audit(
    path: Path = ".",
    json_output: bool = typer.Option(False, "--json", help="JSON output for CI"),
) -> None:
    """Audit GitHub Actions workflows in the given directory."""

    issues: List[Issue] = audit_directory(path)

    if not issues:
        console.print(Panel("[bold green]No issues found! All workflows are clean.[/bold green]"))
        raise typer.Exit(0)

    high_issues = [i for i in issues if i.severity == Severity.HIGH]
    medium_issues = [i for i in issues if i.severity == Severity.MEDIUM]
    low_issues = [i for i in issues if i.severity == Severity.LOW]

    summary = f"High: {len(high_issues)} | Medium: {len(medium_issues)} | Low: {len(low_issues)}"

    if json_output:
        print(json.dumps([i.to_dict() for i in issues], indent=2))
        exit_code = 1 if high_issues else 0
        raise typer.Exit(exit_code)

    table = Table(title="GitHub Actions Audit Results", show_header=True, box=None)
    table.add_column("Severity", style="bold magenta")
    table.add_column("File")
    table.add_column("Rule")
    table.add_column("Message", no_wrap=False)

    for issue in sorted(issues, key=lambda i: (i.severity.value, i.file)):
        sev_color = {"high": "bold red", "medium": "bold yellow", "low": "bold green"}[issue.severity.value]
        table.add_row(
            f"[{sev_color}]{issue.severity}[/{sev_color}]",
            Path(issue.file).name,
            issue.rule,
            issue.message,
        )

    console.print(Panel(table, title=summary))

    exit_code = 1 if high_issues else (0 if not medium_issues else 0)
    raise typer.Exit(exit_code)


if __name__ == "__main__":
    app()
