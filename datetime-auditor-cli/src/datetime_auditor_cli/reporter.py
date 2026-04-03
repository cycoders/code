import json
from pathlib import Path
from typing import List

import rich.console
import rich.table
from rich import print as rprint

from .types import Issue


def report(issues: List[Issue], fmt: str = "table", console: rich.console.Console | None = None) -> None:
    if console is None:
        console = rich.console.Console()

    if not issues:
        console.print("[bold green]No datetime issues found! ✅[/]")
        return

    if fmt == "table":
        _render_table(issues, console)
    elif fmt == "json":
        print(json.dumps([i.__dict__ for i in issues], indent=2, default=str))
    elif fmt == "html":
        _render_html(issues)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    console.print(f"\n[bold red]{len(issues)} issue(s) found.[/]" if len(issues) else "")


def _render_table(issues: List[Issue], console: rich.console.Console) -> None:
    table = rich.table.Table(title="[bold]Datetime Audit Results[/]")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Line:Col", justify="right", style="magenta")
    table.add_column("Severity", justify="right")
    table.add_column("Message", style="white")
    table.add_column("Snippet")

    for issue in issues:
        sev_icon = "🔴" if issue.severity == "error" else "🟡"
        table.add_row(
            str(issue.file.relative_to(Path.cwd())),
            f"{issue.line}:{issue.column}",
            f"{sev_icon} {issue.severity}",
            issue.message,
            issue.snippet or "",
        )

    console.print(table)


def _render_html(issues: List[Issue]) -> None:
    html = '''
<!DOCTYPE html>
<html>
<head>
    <title>Datetime Auditor Report</title>
    <style>
        body { font-family: monospace; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f2f2f2; }
        .error { background-color: #ffebee; }
        .warning { background-color: #fff3e0; }
        pre { margin: 0; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>Datetime Audit Report</h1>
    <table>
        <tr><th>File</th><th>Line</th><th>Col</th><th>Severity</th><th>Message</th><th>Snippet</th></tr>
'''
    for i in issues:
        cls = f" class='{i.severity}'"
        html += f"        <tr{cls}><td>{i.file}</td><td>{i.line}</td><td>{i.column}</td><td>{i.severity.upper()}</td><td>{i.message}</td><td><pre>{i.snippet or ''}</pre></td></tr>\n"
    html += "    </table></body></html>"
    print(html)