import json
import logging
from typing import Dict, Any, List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .models import StraceEvent

logger = logging.getLogger(__name__)

console = Console()

_BAR_WIDTH = 30


def print_summary(stats: Dict[str, Any]):
    """Print rich summary tables."""
    # Top syscalls
    table = Table(title="[bold cyan]Top Syscalls by Time[/]", box=box.ROUNDED)
    table.add_column("Syscall", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Total (s)", justify="right")
    table.add_column("Avg (ms)", justify="right")
    table.add_column("% Time", justify="right")
    table.add_column("Bar")

    for item in stats["top_syscalls"]:
        pct = f"{item['pct_time']:.1f}%"
        avg_ms = item["avg_time"] * 1000
        bar = _render_bar(item["total_time"], max(s.get("total_time", 0) for s in stats["top_syscalls"]))
        table.add_row(
            item["syscall"],
            f"{item['count']:,}",
            f"{item['total_time']:.2f}",
            f"{avg_ms:.2f}",
            pct,
            bar,
        )

    console.print(table)

    # IO summary
    io_panel = Panel(
        f"[bold green]IO Summary[/]\n"
        f"• Total Read: {format_bytes(stats['bytes_read'])} ({stats['bytes_read']:,} B)\n"
        f"• Total Write: {format_bytes(stats['bytes_written'])} ({stats['bytes_written']:,} B)\n"
        f"\nTop Files Opened:\n" + "\n".join(f"  {path}: {count:,}" for path, count in stats["top_file_opens"]),
        title="IO",
    )
    console.print(io_panel)

    # Groups
    groups_table = Table(title="[bold magenta]Syscall Groups[/]")
    groups_table.add_column("Group")
    groups_table.add_column("Count")
    groups_table.add_column("Total Time (s)")
    groups_table.add_column("%")
    for gname, gstats in stats["groups"].items():
        pct = gstats["total_time"] / stats["total_time"] * 100 if stats["total_time"] else 0
        groups_table.add_row(gname, f"{gstats['count']:,}", f"{gstats['total_time']:.2f}", f"{pct:.1f}%")
    console.print(groups_table)


def print_heatmap(events: List[StraceEvent], stats: Dict[str, Any], width: int = 100, height: int = 20):
    """Print ASCII timeline heatmap."""
    if not events:
        console.print("[yellow]No events to visualize[/]")
        return

    min_t = min(e.start_time for e in events)
    max_t = max(e.start_time + (e.duration or 0) for e in events)
    time_range = max_t - min_t

    # Simple density heatmap
    grid = [[" " for _ in range(width)] for _ in range(height)]

    for event in events:
        col = min(int(((event.start_time - min_t) / time_range) * (width - 1)), width - 1)
        dur_norm = min((event.duration or 0) / time_range * height * 5, height - 1)
        row = height - 1 - int(dur_norm)
        for r in range(max(0, row), height):
            grid[r][col] = "█" if r == row else "░"

    console.print(Panel("\n".join("".join(row) for row in grid), title=f"Timeline Heatmap (T={time_range:.2f}s)"))


def print_json(stats: Dict[str, Any]):
    """Print JSON stats."""
    print(json.dumps(stats, indent=2))


def format_bytes(n: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def _render_bar(value: float, max_value: float) -> str:
    if max_value == 0:
        return "░" * _BAR_WIDTH
    filled = int((value / max_value) * _BAR_WIDTH)
    return "█" * filled + "░" * (_BAR_WIDTH - filled)
