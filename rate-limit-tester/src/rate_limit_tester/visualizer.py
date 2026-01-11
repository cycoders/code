from contextlib import contextmanager
import asyncio
from typing import Generator

from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich import box

@contextmanager
def live_dashboard() -> Generator[None, None, None]:
    """Context for live stats display."""
    table = Table(box=box.HEAVY_HEAD)
    table.add_column("Metric")
    table.add_column("Value")

    with Live(Panel(table, title="[bold cyan]Rate Limit Dashboard[/bold cyan]"), refresh_per_second=2) as live:
        yield live
