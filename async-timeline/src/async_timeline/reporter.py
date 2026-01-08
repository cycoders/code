from rich.console import Console, RenderableType
from rich.table import Table
from rich.panel import Panel

from .profiler import AsyncProfiler, TaskTracker
import time


def generate_report(profiler: AsyncProfiler, console: Console):
    # Summary
    n_tasks = len(profiler.tasks)
    n_cancelled = sum(1 for t in profiler.tasks if t.cancelled)
    durations = [t.duration for t in profiler.tasks if t.duration]
    total_dur = sum(durations)
    avg_dur = total_dur / n_tasks if n_tasks else 0

    summary = Panel.fit(
        f"[bold green]Summary[/]\n"
        f"Tasks: [cyan]{n_tasks}[/] Cancelled: [red]{n_cancelled}[/] Peak Concurrency: [magenta]{profiler.max_concurrent}[/]\n"
        f"Avg Duration: [blue]{avg_dur:.3f}s[/] Samples: [dim]{len(profiler.concurrency_history)}[/]",
        title="Stats",
        border_style="green",
    )
    console.print(summary)

    # Slowest tasks
    slow_tasks = sorted(
        [t for t in profiler.tasks if t.duration], key=lambda t: t.duration or 0, reverse=True
    )[:15]
    table = Table(title="Top Slowest Tasks", show_header=True, header_style="bold magenta")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Duration", justify="right", style="yellow")
    table.add_column("Parent", style="dim white")
    table.add_column("Status", justify="right")

    for t in slow_tasks:
        parent_name = t.parent_tracker.name[:25] if t.parent_tracker else "root"
        status = "[red]✗ cancelled[/]" if t.cancelled else "[yellow]⚠ error[/]" if t.exception else "[green]✓ ok[/]"
        table.add_row(t.name[:35], f"{t.duration:.3f}s", parent_name, status)
    console.print(table)

    # Concurrency heatmap
    heatmap_text = _concurrency_heatmap(profiler.concurrency_history, profiler.max_concurrent)
    heatmap_panel = Panel(
        heatmap_text, title="Concurrency Heatmap", subtitle="█ high | ░ low (time →)", border_style="blue"
    )
    console.print(heatmap_panel)

    # Mermaid
    mermaid = profiler.generate_mermaid()
    mermaid_panel = Panel(
        mermaid,
        title="[link=https://mermaid.live]Mermaid Gantt → mermaid.live[/link]",
        expand=False,
    )
    console.print(mermaid_panel)


def _concurrency_heatmap(history: list[int], max_c: int) -> str:
    if not history:
        return "[dim]No concurrency data[/]"

    n_bins = 70
    if len(history) <= n_bins:
        bins = history
    else:
        bin_size = len(history) / n_bins
        bins = [
            max(history[int(i * bin_size) : int((i + 1) * bin_size)] or [0])
            for i in range(n_bins)
        ]

    height = 12
    max_bin = max(bins) or 1
    lines = []
    for h in range(height, 0, -1):
        chars = "".join("█" if (b / max_bin * height) >= h else "░" for b in bins)
        lines.append(chars)
    lines.append("─" * n_bins)
    # Rough timescale
    scale = len(history) / n_bins
    labels = "0s"
    for i in range(10, n_bins, 10):
        ts = int(i * scale * 0.1) / 10
        labels += " " * (10 * 4 - len(str(ts))) + f"{ts}s"
    lines.append(labels[:n_bins])
    return "\n".join(lines)