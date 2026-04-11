import sys
import typer
from pathlib import Path
from typing import Optional

import rich

from . import __version__
from .parsers import parse_csv, parse_json, parse_jsonl
from .stats import compute_stats
from .output import print_stats, print_compare


app = typer.Typer(add_completion=False)
console = rich.Console()

DEFAULT_FIELDS = {
    "ts": "timestamp",
    "duration": "response_time",
    "status": "status_code",
    "endpoint": "endpoint",
    "method": "method",
    "error": "error",
}


@app.command(help="Analyze a load test result file")
def analyze(
    filepath: Path = typer.Argument(..., help="Path to CSV/JSON/JSONL file"),
    fmt: str = typer.Option("csv", "--format", help="Format: csv, json, jsonl"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output JSON file"),
    fields: str = typer.Option(",".join(DEFAULT_FIELDS.values()), "--fields", help="ts,duration,status,endpoint,method,error"),
):
    field_map = dict(zip(DEFAULT_FIELDS.keys(), fields.split(",")))

    # Parse
    if fmt == "csv":
        requests = list(parse_csv(str(filepath), field_map))
    elif fmt == "json":
        requests = list(parse_json(str(filepath), field_map))
    elif fmt == "jsonl":
        requests = list(parse_jsonl(str(filepath), field_map))
    else:
        raise typer.BadParameter(f"Unsupported format: {fmt}")

    if not requests:
        console.print("[red]No valid requests found.[/red]")
        raise typer.Exit(1)

    stats = compute_stats(requests)

    if output:
        output.write_text(rich.json.dumps(stats, indent=2))
        console.print(f"[green]Stats exported to {output}[/green]")
        return

    print_stats(console, stats)


@app.command(help="Compare two result files for regressions")
def compare(
    file1: Path,
    file2: Path,
    fmt1: str = "csv",
    fmt2: str = "csv",
    label1: str = typer.Option("Baseline", "--label1"),
    label2: str = typer.Option("Current", "--label2"),
    fields: str = typer.Option(",".join(DEFAULT_FIELDS.values()), "--fields"),
):
    field_map = dict(zip(DEFAULT_FIELDS.keys(), fields.split(",")))

    # Parse both
    if fmt1 == "csv":
        reqs1 = list(parse_csv(str(file1), field_map))
    # ... similar for json/jsonl
    elif fmt1 == "json":
        reqs1 = list(parse_json(str(file1), field_map))
    elif fmt1 == "jsonl":
        reqs1 = list(parse_jsonl(str(file1), field_map))
    else:
        raise typer.BadParameter(f"Unsupported format: {fmt1}")

    if fmt2 == "csv":
        reqs2 = list(parse_csv(str(file2), field_map))
    elif fmt2 == "json":
        reqs2 = list(parse_json(str(file2), field_map))
    elif fmt2 == "jsonl":
        reqs2 = list(parse_jsonl(str(file2), field_map))
    else:
        raise typer.BadParameter(f"Unsupported format: {fmt2}")

    stats1 = compute_stats(reqs1)
    stats2 = compute_stats(reqs2)

    print_compare(console, stats1, stats2, label1, label2)


@app.command()
def version():
    console.print(f"loadtest-analyzer v{__version__}")


if __name__ == "__main__":
    app()
