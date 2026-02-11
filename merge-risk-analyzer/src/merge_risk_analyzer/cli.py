import typer
from pathlib import Path
from rich.traceback import install

install(show_locals=True, width=Console().width)

from .git_client import GitClient
from .predictor import RiskPredictor
from .renderer import render_json, render_table


app = typer.Typer(
    name="merge-risk-analyzer",
    version="0.1.0",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command(help="Predict merge conflicts between branches.")
def analyze(
    source: str = typer.Argument("HEAD", help="Source branch (default: current)"),
    target: str = typer.Argument("main", help="Target branch (e.g. main/master)"),
    output: str = typer.Option(
        "table", "-o", "--output", help="Format: table (default) or json"
    ),
    repo: Path = typer.Option(
        Path("."),
        "-r",
        "--repo",
        help="Git repo path",
        exists=True,
        file_okay=False,
    ),
) -> None:
    """Analyze merge risk non-destructively."""

    repo = repo.resolve()
    if not repo.is_dir():
        typer.echo(f"Error: '{repo}' is not a directory.", err=True)
        raise typer.Exit(code=1)

    try:
        gc = GitClient(repo)
        risks = RiskPredictor.analyze(gc, source, target)

        if output == "json":
            render_json(risks)
        else:
            render_table(risks)
    except ValueError as ve:
        typer.echo(f"[bold red]Error:[/] {ve}", err=True)
        raise typer.Exit(code=2)
    except git.exc.GitCommandError as ge:
        typer.echo(f"[bold red]Git error:[/] {ge}", err=True)
        raise typer.Exit(code=2)
    except Exception:
        console = typer.Console()
        console.print_exception()
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
