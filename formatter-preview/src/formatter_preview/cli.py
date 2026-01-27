import typer
from pathlib import Path
from typing import List, Optional

from rich.console import Console

from .file_utils import get_candidate_files
from .preview import get_preview_diff, apply_formatter_from_diff


console = Console()
app = typer.Typer(add_completion=False)


@app.command(help="Preview formatting/lint changes")
def preview(
    files: Optional[List[str]] = typer.Argument(None, help="Specific files/dirs"),
    staged: bool = typer.Option(
        False, "--staged", help="Only staged files (git diff --cached)"
    ),
    all_files: bool = typer.Option(
        False, "--all", help="All project files (git ls-files)"
    ),
):
    """Preview diffs from formatters."""
    if files is None:
        candidate_files = get_candidate_files(staged, all_files)
    else:
        candidate_files = []
        for pattern in files:
            p = Path(pattern)
            if p.is_dir():
                candidate_files.extend(p.rglob("*.py") + p.rglob("*.js"))
            elif p.exists():
                candidate_files.append(str(p))

    if not candidate_files:
        console.print("[green]No candidate files found."))
        raise typer.Exit(0)

    changed_files: List[tuple[str, str]] = []
    with typer.progress(
        candidate_files, transient=True, console=console
    ) as progress:
        for task in progress:
            diff = get_preview_diff(Path(task.name))
            if diff:
                changed_files.append((task.name, diff))

    if not changed_files:
        console.print("[green]No formatting/lint changes needed! 🎉")
        raise typer.Exit(0)

    for file_path, diff_text in changed_files:
        from rich.syntax import Syntax
        from rich.panel import Panel

        syntax = Syntax(diff_text, "diff", line_numbers=True, word_wrap=False)
        panel = Panel(
            syntax, title=f"[bold cyan]{file_path}[/bold cyan]", expand=False
        )
        console.print(panel)
        console.print()


@app.command(help="Check if files need changes (CI-friendly)")
def check(
    files: Optional[List[str]] = typer.Argument(None),
    staged: bool = typer.Option(False, "--staged"),
    all_files: bool = typer.Option(False, "--all"),
):
    """Fail if any changes needed."""
    if files is None:
        candidate_files = get_candidate_files(staged, all_files)
    else:
        candidate_files = files  # simplified

    changed_count = 0
    for f in candidate_files:
        if get_preview_diff(Path(f)):
            console.print(f"[yellow]✗ {f} needs changes[/yellow]")
            changed_count += 1

    if changed_count > 0:
        console.print(f"\n[bold red]{changed_count} files need formatting/linting.[/bold red]")
        raise typer.Exit(1)
    console.print("[bold green]✅ All clean![/bold green]")


@app.command(help="Apply changes (destructive!)")
def apply_(
    files: List[str],
    yes: bool = typer.Option(False, "--yes/-y", help="No confirmation"),
):
    """Apply formatting/lint fixes. Use --dry-run first."""
    for file_path in typer.progress(files):
        p = Path(file_path)
        diff = get_preview_diff(p)
        if not diff:
            console.print(f"[green]{p.name}: no changes[/green]")
            continue

        # Show preview
        from rich.syntax import Syntax
        from rich.panel import Panel
        syntax = Syntax(diff, "diff")
        console.print(Panel(syntax, title=p.name))

        if not yes:
            confirm = typer.confirm("Apply changes?", default=False)
            if not confirm:
                console.print("[yellow]Skipped.[/yellow]")
                continue

        # Apply
        apply_formatter_from_diff(p)
        console.print(f"[bold green]Applied to {p.name}! 🎉[/bold green]")


if __name__ == "__main__":
    app()
