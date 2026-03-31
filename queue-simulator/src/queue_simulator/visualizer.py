import json
from rich.console import Console
from rich.table import Table
import plotext as plt
from typing import Dict, Any

from .types import Stats

console = Console()

plt.clc()


def display_table(stats: Stats):
    table = Table(title="[bold cyan]Queue Simulator Results[/bold cyan]", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")

    table.add_row("Avg Latency", f"{stats.avg_latency:.3f}s")
    table.add_row("p95 Latency", f"{stats.p95_latency:.3f}s")
    table.add_row("Max Queue Length", str(stats.max_queue_len))
    table.add_row("Avg Queue Length", f"{stats.avg_queue_len:.2f}")
    table.add_row("Throughput", f"{stats.throughput:.2f} jobs/s")
    table.add_row("Utilization", f"{stats.utilization:.1f}%")
    table.add_row("Total Jobs Completed", str(stats.completed_jobs))
    table.add_row("Avg Service Time", f"{stats.avg_service_time:.3f}s")

    console.print(table)


def display_plots(stats: Stats):
    if not stats.queue_lens:
        console.print("[yellow]No queue data for plotting.[/yellow]")
        return

    # Limit for terminal
    max_points = 2000
    if len(stats.queue_lens) > max_points:
        step = len(stats.queue_lens) // max_points
        q_times = stats.queue_times[::step]
        q_lens = stats.queue_lens[::step]
    else:
        q_times = stats.queue_times
        q_lens = stats.queue_lens

    # Queue length plot
    plt.plot(q_times, q_lens, width=plt.terminal_width(), height=15)
    plt.title("Queue Length Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Queue Length")
    plt.show()

    # Latency histogram
    if stats.latencies:
        plt.histogram(stats.latencies, bins=30, width=plt.terminal_width(), height=15)
        plt.title("Latency Distribution")
        plt.ylabel("Frequency")
        plt.show()


def display_json(stats: Stats):
    print(json.dumps(stats.to_dict(), indent=2))


def show_output(stats: Stats, output: str):
    if "table" in output:
        display_table(stats)
    if "plot" in output:
        display_plots(stats)
    if "json" in output:
        display_json(stats)