import typer
from pathlib import Path
from typing import Optional

import rich.console
import rich.table

from .core import find_unused, AnalysisResult
from .pruner import perform_prune

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = rich.console.Console()


@app.command(help="Scan for unused dependencies")
def check(
    root: Path = typer.Argument(Path('.'), exists=True, file_okay=False),
    requirements: Optional[Path] = typer.Option(
        None, "--requirements", "-r", help="requirements.txt path"
    ),
    poetry: bool = typer.Option(False, "--poetry", help="Force pyproject.toml"),
    verbose: bool = typer.Option(False, "-v"),
):
    stats: AnalysisResult = find_unused(root, requirements, poetry)
    unused_count = len(stats['unused'])
    decl_count = len(stats['declared'])
    used_count = len(stats['used'])

    print(
        f"[bold cyan]Analysis[/]: {decl_count} declared, {used_count} used, "
        f"{unused_count} unused"
    )

    if unused_count == 0:
        print("[green]✓ Clean![/]")
        raise typer.Exit(0)

    table_ = rich.table.Table(title="Unused Dependencies")
    table_.add_column("Package", style="cyan")
    for pkg in sorted(stats['unused']):
        table_.add_row(pkg)
    console.print(table_)

    if verbose:
        print("[dim]Sample used:[/]", ', '.join(sorted(list(stats['used'])[:10])))


@app.command(help="Prune unused (requirements.txt only)")
def prune(
    root: Path = typer.Argument(Path('.'), exists=True, file_okay=False),
    requirements: Path = typer.Option(
        Path('requirements.txt'),
        "--requirements",
        "-r",
        exists=True,
        help="requirements.txt to prune",
    ),
    dry_run: bool = typer.Option(True, "--dry-run/-n"),
    yes: bool = typer.Option(False, "--yes/-y"),
):
    if not requirements.exists():
        print(f"[red]{requirements} not found[/]")
        raise typer.Exit(1)

    stats = find_unused(root, requirements)
    unused_count = len(stats['unused'])
    if unused_count == 0:
        print("[green]Nothing to prune.[/]")
        raise typer.Exit(0)

    if not yes and not typer.confirm(f"Prune {unused_count} deps from {requirements}?"):
        print("[yellow]Aborted.[/]")
        raise typer.Exit(0)

    perform_prune(root, requirements, dry_run)


if __name__ == '__main__':
    app()