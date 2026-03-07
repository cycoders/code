from typing import List
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from .types import Issue

console = Console()


def console_report(issues: List[Issue]) -> None:
    if not issues:
        console.print("[bold green]✓ Perfect! All WCAG checks passed.[/] 🎉")
        return

    table = Table(title="[bold red]WCAG Violations Summary[/]", show_header=True, header_style="bold magenta")
    table.add_column("Severity", style="bold", no_wrap=True)
    table.add_column("Principle", no_wrap=True)
    table.add_column("WCAG", no_wrap=True)
    table.add_column("Count", justify="right")
    table.add_column("ID")

    # Aggregate by severity
    sev_order = {'error': [], 'warning': [], 'info': []}
    for issue in issues:
        sev_order[issue.severity].append(issue)

    for sev, group in sev_order.items():
        if group:
            table.add_row(sev.upper(), '', '', str(len(group)), '')
            for i in group[:3]:  # Top 3 per group
                table.add_row('', i.principle[:15], i.wcag, '', i.id)

    console.print(Panel(table, padding=(1, 2)))

    # Score
    score = issues[0].model_dump().get('score', 'F') if issues else 'A'  # From auditor
    console.print(f"[bold yellow]Overall Score: {score}[/] (Violations: {len(issues)})")

    console.print("\n[bold]Detailed Fixes:[/]\n")
    for issue in sorted(issues, key=lambda i: i.severity):
        style = "red" if issue.severity == "error" else "yellow" if issue.severity == "warning" else "cyan"
        console.print(f"[{style}]{issue.id}[/{style}]: {issue.description}")
        console.print(f"  📋 WCAG {issue.wcag} ({issue.principle}/{issue.level})")
        console.print(f"  💡 Fix: {issue.help}")
        if issue.examples:
            console.print("  📝 Examples:")
            for ex in issue.examples[:2]:
                console.print(f"     • {ex}")
        console.print("")


def json_report(issues: List[Issue]) -> str:
    return json.dumps([i.model_dump() for i in issues], indent=2)


def html_report(issues: List[Issue]) -> str:
    issues_html = ''.join([
        f'<tr class="{i.severity}"><td>{i.id}</td><td>{i.wcag}</td><td>{i.description}</td><td>{i.help}</td><td>{i.count}</td></tr>'
        for i in issues
    ])
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<title>WCAG Audit Report</title>
<style>
body {{font-family:Arial,sans-serif;margin:20px;}} table {{border-collapse:collapse;width:100%;}} th,td {{border:1px solid #ddd;padding:12px;text-align:left;}} th {{background:#f4f4f4;}} .error {{background:#ffebee;}} .warning {{background:#fff3e0;}} .info {{background:#e3f2fd;}}
</style></head>
<body>
<h1>WCAG Audit Report</h1>
<table><thead><tr><th>ID</th><th>WCAG</th><th>Description</th><th>Fix</th><th>Count</th></tr></thead><tbody>{issues_html}</tbody></table>
</body></html>"""
