import sys
import typer
from pathlib import Path
from typing import Optional
import rich.traceback

rich.traceback.install(show_locals=True)


from .git_parser import get_repo_commits
from .stats_calculator import calculate_stats
from .visualizer import print_table, print_json
from .types import ContributorStats


app = typer.Typer()
console = typer.Console()


@app.command(help="Analyze contributor stats in a git repo")
def analyze(
    repo: Path = typer.Argument(Path("."), exists=True, file_okay=False, resolve_path=True, help="Git repository path"),
    since: Optional[str] = typer.Option(None, "--since", help="ISO date (e.g. 2024-01-01)"),
    until: Optional[str] = typer.Option(None, "--until", help="ISO date"),
    author: Optional[str] = typer.Option(None, "--author", help="Filter by author name/email"),
    no_merges: bool = typer.Option(False, "--no-merges", help="Exclude merge commits"),
    output: str = typer.Option("table", "--output", choices=["table", "json"], help="Output format"),
    sort_by: str = typer.Option("net_loc", "--sort-by", choices=["net_loc", "commits", "insertions"], help="Sort key"),
):
    try:
        commits = get_repo_commits(repo, since=since, until=until, author=author, no_merges=no_merges)
        stats: List[ContributorStats] = calculate_stats(commits)

        # Re-sort if needed
        reverse = True
        key_map = {
            "net_loc": lambda s: s.net_loc,
            "commits": lambda s: s.commit_count,
            "insertions": lambda s: s.total_insertions,
        }
        stats.sort(key=key_map[sort_by], reverse=reverse)

        if output == "json":
            print_json(stats)
        else:
            print_table(stats, console)

        if not stats:
            console.print("[yellow]No contributions found.[/yellow]")

    except git.exc.InvalidGitRepositoryError:
        typer.echo("❌ Error: Invalid git repository", err=True)
        raise typer.Exit(code=1)
    except Exception:
        console.print_exception()
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
