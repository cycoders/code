import json
import polars as pl
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.progress import SpinnerColumn, TextColumn, Progress
from plotext import plot, hist, show as plot_show
from typing import Dict, Any
from .suggester import suggest

console = Console()


def show_progress(task: Any):
    with Live(
        Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")),
        refresh_per_second=10,
    ) as live:
        yield live


def print_table(df: pl.DataFrame, sample_queries: Dict[str, str], show_sugs: bool):
    table = Table(title="Slow Query Hotspots")
    table.add_column("FP", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Avg Dur", justify="right")
    table.add_column("Total Dur", justify="right")
    table.add_column("P95", justify="right")
    table.add_column("Sample Query", max_width=60)
    if show_sugs:
        table.add_column("Suggestions", max_width=50)

    for row in df.iter_rows(named=True):
        fp = row["fp"]
        samp_q = sample_queries.get(fp, "N/A")
        sugs = "; ".join(suggest(samp_q)) if show_sugs else ""
        table.add_row(
            fp,
            str(row["count"]),
            f"{row['avg_duration_ms']:.1f}ms",
            f"{row['total_duration_ms']/1000:.2f}s",
            f"{row['p95_ms']:.0f}ms",
            samp_q,
            sugs,
        )
    console.print(table)


def print_histogram(df: pl.DataFrame):
    durations = df["duration_ms"].to_list()
    if durations:
        try:
            hist(durations, bins=25, width=80, height=15)
            plot.title("Query Duration Histogram (ms) | log scale")
            plot_show()
        except:
            console.print("[yellow]Histogram skipped (plotext issue)[/yellow]")


def output_json(df: pl.DataFrame, sample_queries: Dict[str, str]):
    data = df.to_dicts()
    for d in data:
        fp = d["fp"]
        d["sample_query"] = sample_queries.get(fp, "")
    print(json.dumps(data, indent=2))

# CSV via polars
