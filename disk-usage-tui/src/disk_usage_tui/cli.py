import sys
import typer
from pathlib import Path
from typing import Optional

from .app import DiskUsageApp

app = typer.Typer(add_completion=False)

@app.command()
def main(
    path: Path = typer.Argument(Path("."), exists=True, help="Directory to analyze"),
    no_gitignore: bool = typer.Option(
        False, "--no-gitignore", help="Disable .gitignore parsing"
    ),
):
    """Interactive disk usage explorer."""
    try:
        app_instance = DiskUsageApp(path.resolve(), use_gitignore=not no_gitignore)
        app_instance.run()
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from e