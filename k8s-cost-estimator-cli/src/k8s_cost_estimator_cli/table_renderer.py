from rich.console import Console
from rich.table import Table
from rich import box
from itertools import accumulate
from typing import List

from .types import CostBreakdown, Config


console = Console()


def render_table(breakdowns: List[CostBreakdown], cfg: Config):
    table = Table(box=box.ROUNDED_GRID, show_header=True, header_style="bold magenta")
    table.add_column("Namespaced", style="cyan")
    table.add_column("Kind", style="green")
    table.add_column("Name")
    table.add_column("Rpl", justify="right")
    table.add_column("CPU (cores)", justify="right")
    table.add_column("Mem (GiB)", justify="right")
    table.add_column("$/month", justify="right")

    total_cpu = total_mem = total_cost = 0.0
    for b in breakdowns:
        table.add_row(
            f"{b.namespace}",
            b.kind,
            b.name,
            str(b.replicas),
            str(b.cpu_cores),
            str(b.mem_gib),
            f"${b.total_cost}",
        )
        total_cpu += b.cpu_cores
        total_mem += b.mem_gib
        total_cost += b.total_cost

    table.add_row(
        "TOTAL",
        "",
        "",
        "",
        str(round(total_cpu, 2)),
        str(round(total_mem, 2)),
        f"${round(total_cost, 2)}",
    )

    console.print(table)
    console.print(f"[dim]Config: {cfg.provider}/{cfg.region}, {cfg.nodes} nodes, {cfg.utilization*100}% util, {cfg.days} days[/]")
