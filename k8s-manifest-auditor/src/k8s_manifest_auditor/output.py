import json
from typing import List

from rich.console import Console
from rich.table import Table
from rich.json import RichJson

from .types import Issue


console = Console()


def print_table(issues: List[Issue]):
    if not issues:
        console.print("[green]No issues found! ✅[/green]")
        return

    table = Table(title="K8s Manifest Audit", show_header=True, header_style="bold magenta")
    table.add_column("Severity", style="bold", no_wrap=True)
    table.add_column("Resource")
    table.add_column("Issue")
    table.add_column("Field", no_wrap=True)
    table.add_column("Suggestion")

    for issue in issues:
        table.add_row(
            f"[red]{issue.severity}[/red]" if issue.severity == "HIGH" else f"[yellow]{issue.severity}[/yellow]" if issue.severity == "MEDIUM" else issue.severity,
            issue.resource,
            issue.message,
            issue.field,
            issue.suggestion,
        )

    console.print(table)


def print_json(issues: List[Issue]):
    data = [issue.to_dict() for issue in issues]
    console.print(RichJson(json.dumps(data, indent=2)))


def output_issues(issues: List[Issue], fmt: str):
    if fmt == "json":
        print_json(issues)
    else:
        print_table(issues)
