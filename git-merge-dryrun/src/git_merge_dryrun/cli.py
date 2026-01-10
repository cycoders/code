import typer
from pathlib import Path
from rich.console import Console
import sys

from .merger import (
    get_merge_base,
    detect_conflicts,
    get_incoming_commits,
    get_current_graph,
)
from .visualizer import show_merge_preview

app = typer.Typer(add_completion=False, rich_markup_mode="rich")
console = Console()

@app.command(help="Preview merging TARGET into SOURCE (default: current branch/HEAD)")
def merge(
    target: str = typer.Argument(..., help="Branch to merge in"),
    source: str = typer.Argument(None, help="Source branch (default: HEAD)"),
    show_diffs: bool = typer.Option(
        False, "--show-diffs", "-d", help="Show detailed diffs for conflicts"
    ),
):
    """
    Preview the outcome of a git merge without any changes to the repo.

    Detects conflicts, lists incoming commits, shows commit graph, and previews diffs.
    """
    repo_path = Path.cwd()
    if not (repo_path / ".git").exists():
        typer.echo("❌ Not a git repository.", err=True)
        raise typer.Exit(1)

    source = source or "HEAD"

    try:
        base = get_merge_base(repo_path, source, target)
        conflicts = detect_conflicts(repo_path, base, source, target)
        incoming = get_incoming_commits(repo_path, source, target)
        graph = get_current_graph(repo_path)

        show_merge_preview(
            console,
            source,
            target,
            conflicts,
            incoming,
            graph,
            base,
            repo_path,
            show_diffs,
        )
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1) from e

if __name__ == "__main__":
    app()