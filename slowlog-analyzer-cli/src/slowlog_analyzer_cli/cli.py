import sys
import typer
from pathlib import Path
from typing import TextIO

from . import __version__
from .parser import parse_log, detect_format
from .stats import compute_stats
from .visualizer import print_table, print_histogram, output_json, show_progress
from rich.console import Console

console = Console()
app = typer.Typer()

@app.command(no_args_is_help=True)
def main(
    log_file: Path = typer.Argument(..., help="Log file path (- for stdin)"),
    format_: str = typer.Option("auto", "--format", "-f", help="postgres/mysql/auto"),
    min_duration: float = typer.Option(0.0, "--min-duration", help="Filter (ms)"),
    top_n: int = typer.Option(20, "--top", "-n", help="Top queries"),
    output: str = typer.Option("table", "--output", "-o", help="table/json/csv"),
    histogram: bool = typer.Option(False, "--histogram"),
    suggestions: bool = typer.Option(True, "--suggestions/-S"),
    version: bool = typer.Option(False, "--version"),
):
    if version:
        console.print(f"slowlog-analyzer-cli {__version__}")
        raise typer.Exit()

    input_path = str(log_file)
    fmt = format_

    if fmt == "auto":
        fmt = detect_format(input_path)
        console.print(f"[green]Auto-detected format: {fmt}[/green]")

    with show_progress("Parsing log"):
        queries = parse_log(input_path, fmt, min_duration)

    console.print(f"[bold green]Parsed {len(queries)} queries (>= {min_duration}ms)[/bold green]")

    aggs, samples = compute_stats(queries, top_n)

    if output == "table":
        print_table(aggs, samples, suggestions)
    elif output == "json":
        output_json(aggs, samples)
    elif output == "csv":
        print(aggs.write_csv())  # polars
        return

    if histogram:
        print_histogram(aggs)


if __name__ == "main":
    app()
