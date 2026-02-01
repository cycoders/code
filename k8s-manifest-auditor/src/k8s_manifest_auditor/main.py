import logging
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.logging import RichHandler

from .auditor import audit_path
from .output import output_issues


app = typer.Typer(no_args_is_help=True)


@app.command(name="audit")
def cli(
    path: Path = typer.Argument(Path("."), help="Path to manifests directory"),
    format: str = typer.Option("table", "--format", "-f", help="Output format (table/json)"),
    min_severity: str = typer.Option("ALL", "--min-severity", "-s", help="Min severity (ALL/HIGH/MEDIUM/LOW)"),
    verbose: bool = typer.Option(False, "--verbose/-v", help="Verbose logging"),
):
    """
    Audit Kubernetes manifests for issues.
    """
    # Logging
    log_level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    if not path.exists():
        typer.echo(f"Error: Path '{path}' does not exist.", err=True)
        raise typer.Exit(1)

    try:
        issues = audit_path(path, min_severity)
        output_issues(issues, format)
        if issues:
            raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error during audit: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
