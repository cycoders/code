import json
import sys
from pathlib import Path
from typing import Any

import typer
from rich.console import Console

from . import __version__
from .schema_differ import diff_schemas
from .diff_model import DiffIssue
from .reporter import report_diffs
from .compatibility import is_backward_compatible


app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command(help="Diff two schemas and report changes")
def diff(
    old: Path = typer.Argument(..., help="Path to old schema"),
    new: Path = typer.Argument(..., help="Path to new schema"),
    output: str = typer.Option("human", "--output/-o", help="Output: human|json"),
):
    """Generate detailed diff between old and new schema."""

    try:
        with old.open("r") as f:
            schema1 = json.load(f)
        with new.open("r") as f:
            schema2 = json.load(f)
    except json.JSONDecodeError as e:
        typer.echo(f"Invalid JSON in {str(e)}: {e}", err=True)
        raise typer.Exit(1)
    except FileNotFoundError as e:
        typer.echo(f"File not found: {e}", err=True)
        raise typer.Exit(1)

    issues = diff_schemas(schema1, schema2)

    if output == "json":
        print(json.dumps([i.to_dict() for i in issues], indent=2))
    else:
        report_diffs(issues, console)


@app.command(help="Check backward compatibility")
def check(
    old: Path = typer.Argument(..., help="Path to old schema"),
    new: Path = typer.Argument(..., help="Path to new schema"),
    verbose: bool = typer.Option(False, "--verbose/-v", help="Show all issues"),
):
    """Exit 0 if new schema is backward-compatible, else 1 + report."""

    try:
        with old.open("r") as f:
            schema1 = json.load(f)
        with new.open("r") as f:
            schema2 = json.load(f)
    except Exception as e:
        typer.echo(f"Error loading schemas: {e}", err=True)
        raise typer.Exit(1)

    issues = diff_schemas(schema1, schema2)
    compatible = is_backward_compatible(issues)

    if compatible:
        console.print("[green bold]✅ Backward compatible![/green bold]")
        raise typer.Exit(0)
    else:
        console.print("[red bold]❌ Breaking changes detected![/red bold]")
        if verbose:
            report_diffs(issues, console)
        raise typer.Exit(1)


@app.command()
def version():
    """Show version."""
    typer.echo(f"json-schema-diff-cli {__version__}")


if __name__ == "__main__":
    app()