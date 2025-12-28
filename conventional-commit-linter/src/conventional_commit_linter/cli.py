import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from rich.panel import Panel
from git import Repo

from .config import load_config
from .linter import CommitLinter
from .utils import get_git_root, get_git_root_from_msg_file

app = typer.Typer(console=Console())


@app.command(help="Lint commit(s) in a Git revision range")
def lint(revision: str = typer.Argument("HEAD", help="e.g. HEAD~3..HEAD")):
    root = get_git_root()
    config = load_config(root)
    linter = CommitLinter(config)

    repo = Repo(root)
    commits = list(repo.iter_commits(revision))
    if not commits:
        typer.echo("No commits found", err=True)
        raise typer.Exit(1)

    failures = []
    with Progress() as progress:
        task = progress.add_task("[cyan]Linting commits...", total=len(commits))
        for commit in commits:
            result = linter.lint(commit.message)
            if not result.valid:
                failures.append((commit.hexsha[:8], commit.summary, result.errors))
            progress.advance(task)

    if failures:
        table = Table(title="[red]Lint Failures")
        table.add_column("SHA", style="cyan")
        table.add_column("Summary")
        table.add_row("Errors")
        for sha, summary, errors in failures:
            table.add_row(sha, summary, "\n".join(f"  • [red]{e}[/red]" for e in errors))
        typer.echo(table)
        raise typer.Exit(1)
    typer.echo("[green]All commits valid! ✓[/green]")


@app.command(help="Lint single commit message file (for hooks)")
def lint_hook(msg_file: Path):
    """Git commit-msg hook entrypoint."""
    root = get_git_root_from_msg_file(msg_file)
    config = load_config(root)
    linter = CommitLinter(config)

    with open(msg_file) as f:
        message = f.read()

    result = linter.lint(message)
    if not result.valid:
        typer.echo(Panel("\n".join(result.errors), title="[red]Commit rejected[/red]"))
        raise typer.Exit(1)
    sys.exit(0)


@app.command(help="Install Git commit-msg hook")
def install_hook():
    root = get_git_root()
    hook_path = root / ".git/hooks/commit-msg"

    content = "#!/usr/bin/env sh\nexec python3 -m conventional_commit_linter lint-hook \"$1\"\n"

    hook_path.write_text(content)
    hook_path.chmod(0o755)

    typer.echo(f"[green]✓[/green] Installed hook: {hook_path}")


if __name__ == "__main__":
    app()
