import typer
from pathlib import Path
from git import Repo
from .app import BlameApp
from .parser import parse_blame_porcelain

app = typer.Typer(no_args_is_help=True)

@app.command()
def main(
    file: Path = typer.Argument(..., exists=True, readable=True),
    rev: str = typer.Option("HEAD", "--rev", "-r", help="Revision to blame"),
) -> None:
    """Interactive TUI git blame viewer."""
    try:
        repo = Repo(Path.cwd(), search_parent_directories=True)
    except Exception as e:
        typer.echo(f"Error: Not a git repository: {e}", err=True)
        raise typer.Exit(1)

    if file not in repo.tree().traverse():
        typer.echo(f"Error: {file} not in repo or not tracked.", err=True)
        raise typer.Exit(1)

    try:
        porcelain = repo.git.blame(rev, "--porcelain", str(file))
    except Exception as e:
        typer.echo(f"Error running git blame: {e}", err=True)
        raise typer.Exit(1)

    entries = parse_blame_porcelain(porcelain)
    BlameApp(file=file, repo=repo, entries=entries).run()

if __name__ == "__main__":
    app()