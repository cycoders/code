from __future__ import annotations

import typer
from rich.console import Console

from .analyzer import analyze

app = typer.Typer(help="Deep symlink analysis for monorepos")
console = Console()

@app.command()
def main(
    path: str = typer.Argument(".", help="Root directory to scan"),
    format: str = typer.Option("rich", "--format", help="Output format: rich|json|sarif"),
    fail_on: str = typer.Option("cyclic,broken", "--fail-on", help="Comma-separated failure modes"),
):
    """Run symlink analysis."""
    results = analyze(path, fail_on.split(","))
    if format == "rich":
        console.print(results)
    elif format == "json":
        console.print_json(data=results)
    raise typer.Exit(results["exit_code"])