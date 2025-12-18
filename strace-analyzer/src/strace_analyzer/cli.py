import logging
import sys
from pathlib import Path
from typing import Literal

import typer
from rich import print as rprint
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn


from . import __version__
from .parser import parse_strace
from .analyzer import analyze
from .visualizer import print_summary, print_heatmap, print_json


app = typer.Typer(no_args_is_help=True)


@app.command(help="Analyze strace log")
def analyze(
    filename: Path = typer.Argument(..., help="Path to strace.log"),
    output: Literal["summary", "heatmap", "json"] = typer.Option(
        "summary", "--output/-o", help="Output format"
    ),
    width: int = typer.Option(100, "--width", min=50, max=200, help="Heatmap width"),
    filter_: str = typer.Option(
        None, "--filter", help="Regex filter on syscall name"
    ),
    verbose: bool = typer.Option(False, "-v/--verbose"),
):
    if verbose:
        logging.basicConfig(level=logging.DEBUG, handlers=[RichHandler()])

    rprint(f"[bold cyan]Strace Analyzer v{__version__}", end="\n\n")

    # Parse with progress
    events = []
    with Progress(
        SpinnerColumn(), TextColumn("Parsing strace..."), console=typer.rich_console
    ) as progress:
        task = progress.add_task("Parse", total=None)
        events = parse_strace(filename)
        progress.remove_task(task)

    if filter_:
        import re
        pat = re.compile(filter_)
        events = [e for e in events if pat.search(e.syscall)]

    if not events:
        rprint("[yellow]No events found.[/]")
        raise typer.Exit(1)

    stats = analyze(events)

    if output == "summary":
        print_summary(stats)
    elif output == "heatmap":
        print_heatmap(events, stats, width)
    elif output == "json":
        print_json(stats)


if __name__ == "__main__":
    app()
