import json
import sys
from pathlib import Path
from typing import List

import typer
from rich.console import Console

from . import __version__
from .analyzer import analyze_directory
from .reporter import print_table_report, print_json_report

app = typer.Typer(add_completion=False)
console = Console()

@app.command(help="Show help")
def main(
    paths: List[Path] = typer.Argument(Path("."), help="Paths to scan"),
    exclude: List[str] = typer.Option([], "--exclude", help="Exclude patterns (e.g. 'tests/', 'venv/')"),
    fmt: str = typer.Option("table", "--format", "-f", help="Output format: table|json"),
    fail_below: float = typer.Option(0.0, "--fail-below", help="Fail if func coverage % < value"),
    version: bool = typer.Option(False, "--version", help="Show version"),
) -> None:
    if version:
        console.print(f"type-coverage-cli {__version__}")
        raise typer.Exit(0)

    if len(paths) != 1:
        typer.echo("Only one path supported.", err=True)
        raise typer.Exit(1)

    root = paths[0].resolve()
    if not root.is_dir():
        typer.echo(f"'{root}' is not a directory.", err=True)
        raise typer.Exit(1)

    stats = analyze_directory(root, exclude)

    if stats.total_funcs == 0:
        console.print("[yellow]No Python functions found.[/yellow]")
        raise typer.Exit(0)

    func_pct = stats.func_coverage()
    if fail_below > 0 and func_pct < fail_below:
        console.print(f"[red]Func coverage {func_pct:.1f}% < {fail_below}%[/red]")
        raise typer.Exit(1)

    if fmt == "json":
        print_json_report(stats, sys.stdout)
    else:
        print_table_report(stats, console)

if __name__ == "__main__":
    app()