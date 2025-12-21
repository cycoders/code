import typer
from pathlib import Path
from typing_extensions import Annotated
from .blame import collect_blame_data
from .stats import compute_ownership_stats
from .renderer import render_stats
import logging

app = typer.Typer(help="Code Ownership Analyzer", pretty_exceptions_enable=False)

@app.command()
def analyze(
    repo: Path = typer.Argument(Path("."), help="Git repo path"),
    ext: Annotated[list[str], typer.Option(["*"], "--ext")] = ["*"],
    since: str = typer.Option(None, "--since", help="YYYY-MM-DD"),
    top: int = typer.Option(10, "--top"),
    fmt: str = typer.Option("table", "--format", help="table|json|csv"),
    path: Path = typer.Option(Path("."), "--path", help="Subpath filter"),
):
    """Analyze code ownership."""
    logging.basicConfig(level=logging.INFO)
    try:
        blame_data = collect_blame_data(repo, exts=ext, since=since, path=path)
        stats = compute_ownership_stats(blame_data)
        render_stats(stats, top=top, fmt=fmt)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()