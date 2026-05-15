import json
from pathlib import Path
from typing import List

from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.json import JSONRenderer

from .models import Issue, Severity


def report(issues: List[Issue], output: str = "table", file: Optional[Path] = None):
    console = Console(file=file.open("w") if file else None)

    if output == "json":
        data = [i.__dict__ for i in issues]
        json_str = json.dumps(data, indent=2, default=str)
        if file:
            file.write_text(json_str)
        else:
            console.print_json(data)
        return

    if output == "html":
        console = Console(record=True, force_terminal=True)
        _print_rich_report(console, issues)
        html = Console(file=Path(file or "report.html").open("w") if file else None).export_html()
        if file:
            file.write_text(html)
        else:
            print(html)  # fallback
        return

    # table
    _print_rich_report(console, issues)


def _print_rich_report(console: Console, issues: List[Issue]):
    if not issues:
        console.print("[green]No issues found. All keys healthy![/green]")
        return

    # Group by severity
    by_sev = {s: [] for s in Severity}
    for i in issues:
        by_sev[i.severity].append(i)

    for sev in reversed(list(Severity)):
        sev_issues = by_sev[sev]
        if sev_issues:
            table = Table(title=f"{sev.value} Issues ({len(sev_issues)})")
            table.add_column("File", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("FP", style="dim")
            table.add_column("Message", style="white")
            for i in sev_issues:
                fp_short = i.key_info.fingerprint[:16] + "..." if i.key_info.fingerprint else "N/A"
                table.add_row(
                    i.file_path,
                    i.issue_type,
                    fp_short,
                    i.message,
                )
            console.print(table)

    # Summary
    summary = {sev: len(by_sev[sev]) for sev in Severity}
    console.print(Panel.fit(f"Summary: " + " | ".join(f"{k.value}: {v}" for k, v in summary.items()), title="Audit Summary"))
