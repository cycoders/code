import typer
from pathlib import Path
from typing import Optional

import rich.progress

from . import __version__
from .analyzer import analyze_file
from .config import Config, load_config
from .finder import find_python_files
from .reporter import report


app = typer.Typer(add_completion=False)
console = typer.console


@app.command(help="Scan for deadcode")
def scan(
    path: str = typer.Argument(".", help="Root directory to scan"),
    min_confidence: int = typer.Option(
        50, "--min-confidence/-c", min=0, max=100, help="Minimum confidence %"
    ),
    config: Optional[str] = typer.Option(
        None, "--config", help="Custom config file (overrides pyproject.toml)"
    ),
) -> None:
    """Hunt deadcode in Python projects."""

    cfg = load_config(config)

    py_files = list(find_python_files(path, cfg.ignores))
    if not py_files:
        console.print("[yellow]No Python files found.[/]")
        raise typer.Exit(1)

    issues = []
    with rich.progress.Progress(
        rich.progress.TextColumn("[progress.description]{task.description}"),
        rich.progress.BarColumn(),
        rich.progress.TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning files...", total=len(py_files))
        for py_file in py_files:
            issues.extend(analyze_file(py_file))
            progress.advance(task)

    filtered_issues = [i for i in issues if i.confidence >= min_confidence]

    if not filtered_issues:
        console.print("[bold green]✅ No deadcode found above threshold![/]")
        raise typer.Exit(0)

    console.print(f"[bold yellow]Found {len(filtered_issues)} issues >= {min_confidence}%[/]")
    report(filtered_issues)


@app.command()
def version() -> None:
    console.print(f"deadcode-hunter {__version__}")


if __name__ == "__main__":
    app()