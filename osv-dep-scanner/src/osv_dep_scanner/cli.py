import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from .osv_client import scan_lockfile, get_max_severity
from .parsers import parse_lockfile

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def scan(
    path: Path = typer.Argument(..., help="Path to lockfile"),
    output: str = typer.Option("table", "--output", "-o", help="Output format"),
    fail_threshold: str = typer.Option("high", "--fail-threshold", help="Exit 1 if severity met"),
    no_color: bool = typer.Option(False, "--no-color"),
):
    """Scan lockfile for known vulnerabilities via OSV."""

    if no_color:
        console = Console(no_color=True)

    if not path.exists():
        typer.echo(f"Error: {path} does not exist", err=True)
        raise typer.Exit(1)

    with Progress(console=console) as progress:
        task = progress.add_task("[cyan]Parsing lockfile...", total=None)
        deps = parse_lockfile(path)
        progress.remove_task(task)

        if deps:
            task = progress.add_task("[green]Querying OSV...", total=len(deps))
            vuln_by_dep = scan_lockfile(path)
            progress.remove_task(task)
        else:
            vuln_by_dep = {}
            rprint("[yellow]No dependencies found.")

    affected = {k: v for k, v in vuln_by_dep.items() if v}

    if output == "json":
        print(json.dumps(affected, indent=2))
    else:
        _print_table(affected, console)

    if affected:
        max_sev = max(get_max_severity(vs) for vs in affected.values())
        if _SEVERITY_ORDER.get(max_sev, 0) >= _SEVERITY_ORDER.get(fail_threshold.upper(), 2):
            typer.Exit(1)


def _print_table(vuln_by_dep: dict, console: Console):
    if not vuln_by_dep:
        rprint("[green]✅ No vulnerabilities found!")
        return

    table = Table(title="Dependency Vulnerabilities", show_header=True, box=None)
    table.add_column("Package", style="cyan")
    table.add_column("Version")
    table.add_column("Ecosystem")
    table.add_column("Severity", justify="right")
    table.add_column("ID")
    table.add_column("Summary")

    for dep_key, vulns in vuln_by_dep.items():
        ecos, rest = dep_key.split("/", 1)
        name, ver = rest.split("@", 1)
        sev = get_max_sev(vulns)
        sev_color = {
            "CRITICAL": "red",
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "green",
        }.get(sev, "white")
        for vuln in vulns[:3]:  # Top 3 per dep
            table.add_row(
                name,
                ver,
                ecos,
                f"[{sev_color}]{sev}[/{sev_color}]",
                vuln.get("id", ""),
                vuln.get("summary", "")[:80] + "..." if len(vuln.get("summary", "")) > 80 else vuln.get("summary", ""),
            )

    console.print(table)


if __name__ == "__main__":
    app()