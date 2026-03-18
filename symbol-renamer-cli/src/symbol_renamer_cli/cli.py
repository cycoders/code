import typer
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel

from .finder import get_py_files
from .renamer import process_file

app = typer.Typer(add_completion=False)

@app.command(help="Rename symbols across Python files")
def main(  # noqa: main not called
    old_name: str = typer.Argument(..., help="Old symbol name to rename"),
    new_name: str = typer.Argument(..., help="New symbol name"),
    paths: List[str] = typer.Argument(..., help="File(s) or directory(ies) to process"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Simulate changes without writing"),
    preview: bool = typer.Option(True, "--preview", help="Show colorized diffs"),
    output_dir: str = typer.Option(None, "--output-dir", help="Output directory (mirrors structure)"),
    inplace: bool = typer.Option(False, "--inplace", help="Rename in-place with .bak backup"),
) -> None:
    """Safely rename symbols with previews and dry-runs."""
    console = Console()

    path_objs = [Path(p) for p in paths]
    py_files = get_py_files(path_objs, console)

    if not py_files:
        console.print("[red]No Python files found.[/]", err=True)
        raise typer.Exit(1)

    root = path_objs[0] if path_objs and path_objs[0].is_dir() else None
    if output_dir and not root:
        console.print("[yellow]--output-dir requires a directory as first path.[/]", err=True)
        raise typer.Exit(1)

    total_changes = 0
    changed_files = 0

    for file_path in py_files:
        changes = process_file(
            file_path,
            old_name,
            new_name,
            console,
            preview=preview,
            dry_run=dry_run,
            output_dir=output_dir,
            inplace=inplace,
            root=root,
        )
        total_changes += changes
        if changes > 0:
            changed_files += 1

    style = "green" if changed_files > 0 else "blue"
    console.print(
        Panel(
            f"[bold]{changed_files} files changed, {total_changes} identifiers renamed",
            title="Summary",
            border_style=style,
        )
    )

if __name__ == "__main__":
    app()