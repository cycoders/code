import typer
from pathlib import Path
from typing import Optional

from .config import load_config
from .scanner import scan_repos
from .stats import compute_repo_stats
from .table import render_table
from .actions import open_repo, gc_repo

app = typer.Typer(help="Repo Inventory CLI", add_completion=False)

@app.command(help="List repos with stats")
def list_cmd(
    sort: str = typer.Argument("path", help="Sort key: path, commits, branches, size, last_commit"),
    dirty: bool = typer.Option(False, "--dirty", help="Dirty repos only"),
    orphaned: bool = typer.Option(False, "--orphaned", help="No remotes only"),
):
    config = load_config()
    repos = scan_repos(config["paths"], config["excludes"])

    if dirty:
        repos = [r for r in repos if r.is_dirty]
    if orphaned:
        repos = [r for r in repos if r.remote_count == 0]

    sort_key = {
        "path": lambda r: r.path.lower(),
        "commits": lambda r: r.commit_count,
        "branches": lambda r: r.branch_count,
        "size": lambda r: r.raw_git_size,
        "last_commit": lambda r: r.last_commit_date,
    }.get(sort, lambda r: r.path.lower())

    repos.sort(key=sort_key, reverse=(sort != "path"))
    render_table(repos)
    typer.echo(f"\n\u{1F4DD} Total: {len(repos)} repositories", fg=typer.colors.GREEN)

@app.command(help="Open repo in editor")
def open_cmd(
    name_or_path: str,
    editor: Optional[str] = typer.Option("code", help="Editor: code, vim, nano"),
):
    config = load_config()
    repos = scan_repos(config["paths"], config["excludes"])

    for repo in repos:
        if name_or_path == Path(repo.abs_path).name or name_or_path in repo.path:
            open_repo(repo.abs_path, editor)
            return
    typer.echo(f"\u274C Repo '{name_or_path}' not found", fg=typer.colors.RED)

@app.command(help="Git GC repo")
def gc_cmd(
    name_or_path: str,
    aggressive: bool = typer.Option(False, "--aggressive", help="Aggressive GC"),
):
    config = load_config()
    repos = scan_repos(config["paths"], config["excludes"])

    for repo in repos:
        if name_or_path == Path(repo.abs_path).name or name_or_path in repo.path:
            gc_repo(repo.abs_path, aggressive)
            typer.echo(f"\u2705 GC complete: {repo.path}", fg=typer.colors.GREEN)
            return
    typer.echo(f"\u274C Repo '{name_or_path}' not found", fg=typer.colors.RED)

if __name__ == "__main__":
    app()