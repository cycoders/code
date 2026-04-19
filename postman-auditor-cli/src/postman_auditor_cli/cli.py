import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.progress import Progress


from . import __version__
from .models import Collection, ValidationError

from .auditor import Auditor

from .reporter import Reporter


app = typer.Typer(name="postman-auditor-cli", add_completion=False)


@app.command()
def audit(
    file_path: Path = typer.Argument(..., exists=True, dir_okay=False),
    format: str = typer.Option("table", "--format", "f", help="Output format (table/json)"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file (stdout if none)"),
    fail_level: str = typer.Option("error", "--fail-level", help="Fail exit on: error|warning|info"),
    version: bool = typer.Option(False, "--version", help="Show version"),
):
    """Audit a Postman collection for issues."""
    if version:
        print(__version__)
        raise typer.Exit(0)

    # Read & validate
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        collection = Collection.model_validate(data)
    except json.JSONDecodeError as e:
        typer.echo(f"Error: Invalid JSON: {e}", err=True)
        raise typer.Exit(1)
    except ValidationError as e:
        typer.echo(f"Error: Invalid Postman schema: {e}", err=True)
        raise typer.Exit(1)

    # Audit
    with Progress() as progress:
        task = progress.add_task("[cyan]Auditing...", total=None)
        issues = Auditor.audit(collection)
        progress.remove_task(task)

    # Report
    out_file = open(output, "w") if output else sys.stdout
    try:
        Reporter.report(issues, format, out_file)
    finally:
        if output:
            out_file.close()

    # Fail logic
    if issues:
        levels = {"error": 3, "warning": 2, "info": 1}
        max_level = max(levels[i.severity] for i in issues)
        fail_level_val = levels[fail_level]
        if max_level >= fail_level_val:
            raise typer.Exit(1)


if __name__ == "__main__":
    app()
