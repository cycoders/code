import typer
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from .parser import load_manifests
from .differ import compute_resource_diffs, DEFAULT_IGNORES
from .printer import print_diff_summary

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = Console()

@app.command(help="Diff two manifests or directories")
def diff(
    before: Path = typer.Argument(..., help="Before manifest/dir"),
    after: Path = typer.Argument(..., help="After manifest/dir"),
    ignore_field: List[str] = typer.Option(
        [], "--ignore-field", "-i", help="Ignore path (repeatable, e.g. status)"
    ),
    verbose: bool = typer.Option(False, "--verbose/-v", help="Verbose output"),
) -> None:
    """Visualize manifest differences."""
    if not before.exists():
        typer.echo(f"Error: {before} not found", err=True)
        raise typer.Exit(1)
    if not after.exists():
        typer.echo(f"Error: {after} not found", err=True)
        raise typer.Exit(1)

    ignores = DEFAULT_IGNORES + ignore_field

    try:
        before_resources = load_manifests([before])
        after_resources = load_manifests([after])
        diffs = compute_resource_diffs(before_resources, after_resources, ignores)
        print_diff_summary(diffs, console, verbose)

        if not any(diffs.values()):
            console.print("[green]✅ No changes detected[/green]")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()