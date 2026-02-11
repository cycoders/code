import humanize
from datetime import datetime, timezone
from rich.console import Console
from rich.table import Table
from typing import List

from .models import RepoInfo

console = Console()


def render_table(repos: List[RepoInfo]) -> None:
    if not repos:
        console.print("[yellow]No repositories found.[/yellow]")
        return

    table = Table(title="[bold cyan]Local Git Repositories[/bold cyan]", show_header=True, header_style="bold magenta")
    table.add_column("Path", style="cyan", no_wrap=False)
    table.add_column("Status", justify="center")
    table.add_column("Branch", justify="center")
    table.add_column("Age", justify="center")
    table.add_column("Commits", justify="right")
    table.add_column("Branches", justify="right")
    table.add_column("Size", justify="right")
    table.add_column("Languages", justify="center")

    now = datetime.now(timezone.utc)
    for repo in repos[:100]:  # Cap for perf
        status_icon = "[red]🔴[/red]" if repo.is_dirty else "[green]🟢[/green]"
        age = humanize.naturaltime(now - repo.last_commit_date.astimezone(timezone.utc))
        size_str = humanize.naturalsize(repo.raw_git_size)
        langs = ", ".join(repo.top_languages) or "?"

        table.add_row(
            repo.path[-60:] + "..." if len(repo.path) > 60 else repo.path,
            status_icon,
            repo.current_branch,
            age,
            str(repo.commit_count),
            str(repo.branch_count),
            size_str,
            langs,
        )

    console.print(table)
