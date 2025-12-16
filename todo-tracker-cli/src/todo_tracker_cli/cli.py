import os
import sys
from pathlib import Path
from typing import List

import typer
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    SpinnerColumn,
)

import tomli

from . import __version__
from .scanner import scan
from .analyzer import analyze_todos
from .reporter import report


app = typer.Typer(add_completion=False)


def version_callback(value: bool):
    if value:
        typer.echo(f"todo-tracker-cli {__version__}")
        raise typer.Exit()


@app.command(help="Scan codebase for todos and generate reports.")
def main(
    path: Path = typer.Argument(Path('.'), help="Directory to scan"),
    ignore: List[str] = typer.Option([], "--ignore", help="Additional glob patterns to ignore"),
    config: Path = typer.Option(None, "--config", help="TOML config file"),
    fmt: str = typer.Option("table", "--format", help="Output format: table|csv|mermaid"),
    output: str = typer.Option(None, "--output", help="Output file"),
    version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=True),
):
    """Track TODOs, FIXMEs, HACKs with Git age analysis."""

    # Load config
    cfg_ignore = []
    cfg_tags = None
    if config and config.exists():
        with open(config, 'rb') as f:
            cfg = tomli.load(f)
            cfg_ignore = cfg.get('ignore_globs', [])
            cfg_tags = cfg.get('custom_tags')

    ignores = cfg_ignore + ignore
    tags = cfg_tags or None

    root = path.resolve()

    # Scan with progress
    todos: List['TodoItem'] = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
    ) as progress:
        task_scan = progress.add_task("Scanning files...", total=None)

        todos_gen = scan(root, ignores, tags)
        todos = list(todos_gen)
        progress.update(task_scan, completed=len(todos))

    if not todos:
        typer.echo("No todos found.")
        raise typer.Exit(0)

    # Analyze
    task_analyze = progress.add_task("Analyzing with Git...", total=len(todos))
    todos = analyze_todos(todos, str(root))
    progress.update(task_analyze, completed=len(todos))

    # Report
    report(todos, fmt=fmt, output=output)


if __name__ == "__main__":
    app()