import typer
from pathlib import Path
import tomllib
import os
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from .config import get_config_path, load_config
from .worktree import (
    list_worktrees,
    create_worktree,
    switch_worktree,
    prune_worktrees,
    is_git_repo,
)

app = typer.Typer(
    name="git-worktree-manager",
    help="Streamline Git worktree management with rich UI and automation.",
    add_completion=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    pretty_exceptions_enable=False,
)

console = Console()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, version: bool = typer.Option(..., "--version", "-V", is_eager=True)):
    if ctx.invoked_subcommand is None:
        if version:
            rprint(f"[bold cyan]git-worktree-manager[/] v{__import__("__main__").__version__}")
            raise typer.Exit(0)
        ctx.invoke(list)

@app.command(name="list", help="List worktrees with rich status overview.")
def cmd_list(json_output: bool = typer.Option(False, "--json")):
    if not is_git_repo():
        typer.echo("[!] Not a Git repository (git >= 2.5 required).", err=True)
        raise typer.Exit(1)
    config = load_config()
    wts = list_worktrees(config)
    if json_output:
        import json
        print(json.dumps([{k: v for k, v in wt.items() if k != "path"} for wt in wts], indent=2))
        return
    table = Table(title="Git Worktrees", box="heavy", show_lines=True)
    table.add_column("Path", style="cyan", no_wrap=True)
    table.add_column("Branch", style="green")
    table.add_column("Commit", style="yellow", no_wrap=True)
    table.add_column("Status", style="magenta", justify="right")
    for wt in wts:
        rel_path = wt["rel_path"]
        branch = wt.get("branch", wt.get("headrefs", "detached") or "unknown")
        commit = wt.get("commit", "")
        ahead, behind, dirty = wt.get("ahead", 0), wt.get("behind", 0), wt.get("dirty", 0)
        status = f"{ahead}+/{behind}- {'●'*min(dirty,3) if dirty else '○'}"
        table.add_row(rel_path, branch, commit, status)
    console.print(table)

@app.command(help="Create new worktree with smart naming/branching.")
def create(
    name: str = typer.Argument(..., help="Branch name (e.g., feat/login)"),
    from_ref: str = typer.Option(None, "--from/-f", help="Start point (default: config)"),
    dry_run: bool = typer.Option(False, "--dry"),
):
    if not is_git_repo():
        raise typer.Exit(1)
    config = load_config()
    if dry_run:
        typer.echo(f"[dry] Would create '{name}' from {from_ref or config.get('core', {}).get('default_from', 'HEAD')}")
        return
    create_worktree(name, from_ref, config)

@app.command(help="Print cd path for worktree (by path/branch).")
def switch(identifier: str = typer.Argument(..., help="Worktree path or branch")):
    if not is_git_repo():
        raise typer.Exit(1)
    config = load_config()
    wts = list_worktrees(config)
    switch_worktree(identifier, wts)

@app.command(help="Prune stale/removed worktrees.")
def prune(
    dry_run: bool = typer.Option(True, "--dry-run/-n"),
    stale_days: int = typer.Option(30, "--stale-days"),
):
    if not is_git_repo():
        raise typer.Exit(1)
    config = load_config()
    prune_worktrees(dry_run, stale_days, config)

if __name__ == "__main__":
    app()