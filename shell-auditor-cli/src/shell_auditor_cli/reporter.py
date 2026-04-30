import json
from collections import Counter
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table

from .types import AuditResult, Issue


console = Console()


SEV_COLORS = {
    "critical": "red",
    "high": "yellow",
    "medium": "blue",
    "low": "green",
    "info": "white",
}
SEV_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}


def report(result: AuditResult, output: str = "rich") -> None:
    path = result.path

    if output == "rich":
        _report_rich(result)
    elif output == "json":
        issues_data = [{
            "rule_id": i.rule_id,
            "line": i.line,
            "column": i.column,
            "message": i.message,
            "severity": i.severity,
            "fix": i.fix,
        } for i in result.issues]
        print(json.dumps(issues_data, indent=2))
    elif output == "md":
        if result.parse_errors:
            print("## Parse Errors")
            for err in result.parse_errors:
                print(f"- {err}")
        if not result.issues:
            print("## No issues")
            return
        print("## Issues")
        print("| Severity | Rule | Line:Col | Message | Fix |")
        print("|----------|------|----------|---------|-----|")
        for i in sorted(result.issues, key=lambda x: (SEV_ORDER[x.severity], x.line)):
            fix = i.fix or ""
            print(
                f"| {i.severity} | {i.rule_id} | {i.line}:{i.column} | {i.message} | {fix[:50]}{'...' if len(fix)>50 else ''} |"
            )
        print("\n## Summary")
        print(Counter(i.severity for i in result.issues))
    else:
        raise ValueError(f"Unknown output: {output}")


def _report_rich(result: AuditResult) -> None:
    if result.parse_errors:
        console.print("[red]Parse errors:[/red]")
        for err in result.parse_errors:
            console.print(f"  [dim]{err}[/]")

    issues = result.issues
    if not issues:
        console.print("[green]✅ No issues found![/green]")
        return

    table = Table(title=f"Audit: [blue]{result.path}[/blue]")
    table.add_column("Severity", style="cyan")
    table.add_column("Rule")
    table.add_column("Line:Col")
    table.add_column("Message")
    table.add_column("Fix", no_wrap=True)

    for i in sorted(issues, key=lambda x: (SEV_ORDER[x.severity], x.line)):
        sev_style = SEV_COLORS.get(i.severity, "white")
        fix = (i.fix or "")[:60] + "..." if i.fix and len(i.fix) > 60 else i.fix or ""
        table.add_row(
            f"[{sev_style} bold]{i.severity}[/{sev_style}]",
            i.rule_id,
            f"{i.line}:{i.column}",
            i.message,
            fix,
        )

    console.print(table)

    sev_count = Counter(i.severity for i in issues)
    console.print("\n[bold green]Summary:[/bold green]", sev_count)