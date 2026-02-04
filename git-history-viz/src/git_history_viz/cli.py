import sys
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.table import Table

from .parser import parse_repo
from .graph import topological_sort
from .renderer import render_mermaid, render_html

app = typer.Typer(add_completion=False)
console = Console()

@app.command()
def visualize(
    repo_path: Path = typer.Argument(Path("."), help="Path to Git repository"),
    refs: List[str] = typer.Option([], "--ref/-r", help="Git refs (branches/tags)"),
    max_commits: int = typer.Option(500, "--max-commits/-m", min=1, max=50000),
    output: Optional[Path] = typer.Option(None, "--output/-o"),
    fmt: str = typer.Option("html", "--format/-f", choices=["mermaid", "html"]),
    theme: str = typer.Option("default", "--theme/-t"),
    open_: bool = typer.Option(False, "--open/-O"),
):
    """Visualize Git history as interactive Mermaid diagram."""

    repo_path = repo_path.resolve()
    if not repo_path.is_dir():
        print(f"Error: '{repo_path}' is not a directory", file=sys.stderr)
        raise typer.Exit(code=1)

    try:
        commits = parse_repo(str(repo_path), refs or None, max_commits)
        if not commits:
            console.print("[yellow]No commits found in repository.[/yellow]")
            raise typer.Exit(code=1)

        order = topological_sort(commits)
        diagram = render_mermaid(commits, order, theme)

        content = render_html(diagram, theme) if fmt == "html" else diagram

        if output:
            output.write_text(content, encoding="utf-8")
            console.print(f"[green]Saved to [bold]{output}[/bold][/green]")
            if open_ and fmt == "html":
                import webbrowser
                webbrowser.open(f"file://{output.absolute()}")
        else:
            print(content)

        _show_summary(commits)

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        console.print_exception(show_locals=False)
        raise typer.Exit(code=1)


def _show_summary(commits: dict):
    """Print rich summary table."""
    table = Table(title="Repository History Summary", box=None)
    table.add_column("Commits", style="cyan")
    table.add_column("Date Range", style="magenta")
    table.add_column("Unique Authors", style="green")

    nodes = list(commits.values())
    dates = sorted(set(n.date for n in nodes))
    authors = sorted(set(n.author for n in nodes))

    date_range = f"{dates[0]} → {dates[-1]}" if len(dates) > 1 else dates[0]
    authors_str = ", ".join(authors[:3]) + "..." if len(authors) > 3 else ", ".join(authors)

    table.add_row(str(len(commits)), date_range, authors_str)
    console.print(table)
