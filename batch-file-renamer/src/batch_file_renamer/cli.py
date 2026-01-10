import typer
from pathlib import Path
from typing import Optional, List

from rich.console import Console

from .config import load_rules
from .renamer import (
    preview_renames,
    print_preview,
    perform_apply,
    perform_undo,
    get_candidate_files,
)


app = typer.Typer(help="Batch File Renamer: powerful, safe file renaming.")
console = Console()


@app.command(help="Rich preview table (dry-run)")
def preview(
    root: str = typer.Argument(".", help="Root directory"),
    config_file: Optional[str] = typer.Option(None, "-c", "--config", help="Rules YAML"),
    sort_by: str = typer.Option("name", "--sort", choices=["name", "mtime", "size"]),
    include: List[str] = typer.Option([], "--include"),
    exclude: List[str] = typer.Option([], "--exclude"),
):
    root_path = Path(root)
    if not root_path.exists():
        console.print(f"[red]{root} not found.[/]")
        raise typer.Exit(1)

    rules = load_rules(config_file)
    if not rules:
        console.print("[yellow]No rules provided.[/]")
        raise typer.Exit(1)

    renames = preview_renames(root_path, rules, sort_by, include, exclude, console)
    print_preview(renames, console)


@app.command(help="Preview + apply renames")
def apply_cmd(  # renamed to avoid keyword conflict
    root: str = typer.Argument("."),
    config_file: Optional[str] = typer.Option(None, "-c", "--config"),
    resolve: str = typer.Option("append", "--resolve", choices=["append", "overwrite", "skip"]),
    yes: bool = typer.Option(False, "-y", "--yes", help="No confirmation"),
    sort_by: str = typer.Option("name", "--sort", choices=["name", "mtime", "size"]),
    include: List[str] = typer.Option([], "--include"),
    exclude: List[str] = typer.Option([], "--exclude"),
):
    root_path = Path(root)
    rules = load_rules(config_file)
    if not rules:
        console.print("[yellow]No rules.[/]", err=True)
        raise typer.Exit(1)

    renames = preview_renames(root_path, rules, sort_by, include, exclude, console)
    print_preview(renames, console)

    if not yes:
        if not typer.confirm("Proceed with rename?"):
            raise typer.Exit(0)

    perform_apply(root_path, renames, resolve, console)


@app.command(help="Restore from last log/backups")
def undo(root: str = typer.Argument(".")):
    root_path = Path(root)
    perform_undo(root_path, console)


if __name__ == "__main__":
    app()