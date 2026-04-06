import json
from typing import List

from rich.console import Console
from rich.table import Table
from rich import box

from jinja2 import Template

from .models import Issue


console = Console()


def report_console(issues: List[Issue]) -> None:
    """Print rich console report."""
    if not issues:
        console.print("[bold green]✓ No issues found![/]")
        return

    table = Table(title="[bold]OpenAPI Audit Report[/]", box=box.ROUNDED)
    table.add_column("Path", style="cyan", no_wrap=True)
    table.add_column("Rule", style="magenta")
    table.add_column("Severity", style="bold")
    table.add_column("Message")
    table.add_column("Suggestion")

    for issue in issues:
        path_str = " → ".join(issue.path)
        sev_color = "red" if issue.severity == "error" else "yellow" if issue.severity == "warn" else "green"
        table.add_row(
            path_str,
            issue.rule_id,
            f"[{sev_color}]{issue.severity.upper()}[/]",
            issue.message,
            issue.suggestion or "",
        )

    console.print(table)

    # Summary
    counts = {
        sev: len([i for i in issues if i.severity == sev])
        for sev in ('error', 'warn', 'info')
    }
    summary = f"[bold]Summary:[/] {counts['error']} errors, {counts['warn']} warnings, {counts['info']} info"
    console.print(summary)


def report_json(issues: List[Issue]) -> str:
    """Generate JSON report."""
    return json.dumps([{
        'path': issue.path,
        'rule_id': issue.rule_id,
        'message': issue.message,
        'severity': issue.severity,
        'suggestion': issue.suggestion,
    } for issue in issues], indent=2)


def generate_html(issues: List[Issue]) -> str:
    """Generate HTML report using Jinja."""
    template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>OpenAPI Audit Report</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #f4f4f4; font-weight: bold; }
        tr:nth-child(even) { background-color: #f9f9f9; }
        .error { background-color: #ffebee; color: #c62828; }
        .warn { background-color: #fff3e0; color: #ef6c00; }
        .info { background-color: #e3f2fd; color: #1976d2; }
        .summary { margin-top: 20px; font-size: 1.1em; font-weight: bold; }
    </style>
</head>
<body>
    <h1>OpenAPI Audit Report</h1>
    <table>
        <thead>
            <tr>
                <th>Path</th><th>Rule</th><th>Severity</th><th>Message</th><th>Suggestion</th>
            </tr>
        </thead>
        <tbody>
            {% for issue in issues %}
            <tr class="{{ issue.severity }}">
                <td>{{ issue.path | join(' → ') }}</td>
                <td>{{ issue.rule_id }}</td>
                <td>{{ issue.severity.upper() }}</td>
                <td>{{ issue.message }}</td>
                <td>{{ issue.suggestion or '' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <div class="summary">
        Summary: {{ counts.error }} errors, {{ counts.warn }} warnings, {{ counts.info }} info
    </div>
</body>
</html>
    """
    counts = {sev: len([i for i in issues if i.severity == sev]) for sev in ('error', 'warn', 'info')}
    t = Template(template_str)
    return t.render(issues=issues, counts=counts)


def generate_markdown(issues: List[Issue]) -> str:
    """Generate Markdown report."""
    if not issues:
        return "# OpenAPI Audit\n\n✓ No issues found!"
    md = ["# OpenAPI Audit Report", "", "| Path | Rule | Severity | Message | Suggestion |"]
    md.append("|------|------|----------|---------|------------|")
    for issue in issues:
        path_str = " → ".join(issue.path)
        md.append(f"| {path_str} | {issue.rule_id} | {issue.severity.upper()} | {issue.message} | {issue.suggestion or ''} |")
    counts = {sev: len([i for i in issues if i.severity == sev]) for sev in ('error', 'warn', 'info')}
    md.append(f"\n**Summary**: {counts['error']} errors, {counts['warn']} warnings, {counts['info']} info")
    return "\n".join(md)
