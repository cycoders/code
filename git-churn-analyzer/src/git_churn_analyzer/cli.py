import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from typer import Typer

from . import __version__
from .analyzer import analyze_commits
from .output import render_stats
from .parser import parse_git_log


app = Typer(
    name="git-churn-analyzer",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.command()
def version():
    """Show version."""
    typer.echo(f"git-churn-analyzer {__version__}")


@app.command()
def analyze(  # noqa: PLR0913
    since: Optional[str] = typer.Option(
        None, "--since", help="e.g. '2024-01-01' or '90.days'"
    ),
    until: Optional[str] = typer.Option(None, "--until"),
    branch: Optional[str] = typer.Option(None, "--branch"),
    recent_days: int = typer.Option(30, "--recent-days", min=1),
    output: Optional[Path] = typer.Option(
        None, "--output/-o", help="File path or - for stdout"
    ),
    fmt: str = typer.Option("terminal", "--format/-f", help="terminal|json|csv|html"),
    repo: Path = typer.Option(Path("."), "--repo", exists=True, file_okay=False),
):
    """
    Analyze churn in git repo.
    """
    if not repo.is_dir():
        typer.echo(f"Error: {repo} is not a directory", err=True)
        raise typer.Exit(1)

    git_args = [
        "git",
        "log",
        "--numstat",
        "--pretty=format:%H\\t%at\\t%an\\t%s",
    ]

    if since:
        git_args.extend(["--since", since])
    if until:
        git_args.extend(["--until", until])
    if branch:
        git_args.extend(["--branches", branch])

    try:
        raw_output = subprocess.check_output(
            git_args, cwd=repo, stderr=subprocess.DEVNULL, text=True, encoding="utf-8", errors="ignore"
        )
    except FileNotFoundError:
        typer.echo("Error: 'git' command not found", err=True)
        raise typer.Exit(1)
    except subprocess.CalledProcessError:
        typer.echo(f"Error: Invalid git repo/args in {repo}. Run 'git status' first?", err=True)
        raise typer.Exit(1)

    commits = parse_git_log(raw_output)
    if not commits:
        typer.echo("No commits found matching criteria.", err=True)
        raise typer.Exit(1)

    stats = analyze_commits(commits, recent_days)

    outpath = output or Path("-")
    render_stats(stats, fmt.lower(), outpath)


if __name__ == "__main__":
    app()
