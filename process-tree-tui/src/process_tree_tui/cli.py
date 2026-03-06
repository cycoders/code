import sys
from typing import Annotated

import typer
from textual.config import Backend

from .app import ProcessTreeApp

app = typer.Typer(add_completion=False, invoke_without_command=True, no_args_is_help=True)

@app.command()
def main(
    refresh: Annotated[float, typer.Option("--refresh", "-r", min=0.1, help="Refresh interval in seconds")] = 0.5,
    search: Annotated[str, typer.Option("--search", "-s", help="Initial search filter")] = "",
    backend: Backend = typer.Option(Backend.auto, "--backend", help="Textual backend"),
) -> None:
    """Interactive process tree viewer with live metrics and controls."""
    try:
        ProcessTreeApp(refresh_interval=refresh, initial_search=search).run(backend=backend)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e

if __name__ == "__main__":
    app()