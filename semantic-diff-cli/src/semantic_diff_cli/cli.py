'''Main CLI entrypoint.''' 

import typer
from pathlib import Path
from rich.console import Console

console = Console()

from .diff_engine import print_semantic_diff
from .git_utils import perform_git_semdiff

app = typer.Typer(
    name="semantic-diff-cli",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"],
                      "max_content_width": 120},
)


@app.command()
def files(
    old: Path = typer.Argument(..., help="Old version file"),
    new: Path = typer.Argument(..., help="New version file"),
):
    """Generate semantic diff between two files."""
    if not old.is_file():
        raise typer.BadParameter(f"'{old}' does not exist")
    if not new.is_file():
        raise typer.BadParameter(f"'{new}' does not exist")

    content_old = old.read_text(encoding="utf-8", errors="replace")
    content_new = new.read_text(encoding="utf-8", errors="replace")

    print_semantic_diff(str(old), content_old, content_new)


@app.command()
def git(
    base: str = typer.Argument(..., help="Base revision (e.g. 'main')"),
    head: str = typer.Argument(..., help="Head revision (e.g. 'HEAD')"),
    repo: Path = typer.Option(Path("."), "--repo/-C", help="Git repo path"),
    only_text: bool = typer.Option(False, "--only-text", help="Skip binary files"),
):
    """Generate semantic diffs for changed files between git revisions."""
    if not repo.is_dir():
        raise typer.BadParameter(f"'{repo}' is not a directory")

    perform_git_semdiff(base, head, repo, only_text)


if __name__ == "__main__":
    app()
