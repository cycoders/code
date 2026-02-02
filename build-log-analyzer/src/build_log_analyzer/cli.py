import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.traceback import install

install(show_locals=False)

from .parsers import parse_log
from .renderer import render_summary
from .comparator import compare_summaries

app = typer.Typer(add_completion=False)
console = Console(file=sys.stderr)


@app.command(help="Analyze a build log file.")
def analyze(
    log_file: Path = typer.Argument(..., help="Path to log"),
    parser: str = typer.Option("auto", "--parser", help="Parser (auto/docker/npm/etc)"),
    json_output: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Extract timings/errors from a single log."""
    try:
        summary = parse_log(log_file, parser)
        if json_output:
            print(summary.model_dump_json(indent=2))
        else:
            render_summary(summary, console)
    except Exception as e:
        console.print(f"[red bold]Error:[/] {e}", file=sys.stderr)
        raise typer.Exit(code=1) from e


@app.command(help="Compare two logs for regressions.")
def compare(
    log_file1: Path = typer.Argument(..., help="Baseline log"),
    log_file2: Path = typer.Argument(..., help="Comparison log"),
    parser: Optional[str] = typer.Option(None, "--parser"),
):
    """Diff two logs, highlight slowdowns."""
    try:
        s1 = parse_log(log_file1, parser or "auto")
        s2 = parse_log(log_file2, parser or "auto")
        compare_summaries(s1, s2, console)
    except Exception as e:
        console.print(f"[red bold]Error:[/] {e}", file=sys.stderr)
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()