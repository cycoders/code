import time
from typing import Any

from rich.live import Live
from rich.layout import Layout
from rich.table import Table, Column
from rich.panel import Panel
from rich.console import RenderableType
from rich.text import Text
from rich import box

from .simulator import Simulator


def run_live_sim(sim: Simulator, duration: int, tick_delay: float) -> None:
    """Run real-time TUI visualization."""

    layout = Layout()
    layout.split_row(
        Layout(name="states", ratio=2),
        Layout(name="side", ratio=1),
    )
    layout["side"].split_column(
        Layout(name="stats", size=8),
        Layout(name="events", ratio=1),
    )

    def make_layout() -> RenderableType:
        # States table
        table = Table(
            title=f"Node States @ t={sim.tick}", box=box.ROUNDED, expand=True
        )
        table.add_column("Node", style="cyan bold", min_width=8)
        table.add_column("State", style="magenta bold")
        table.add_column("Term", justify="right")
        table.add_column("Voted", justify="right")
        table.add_column("Votes", justify="right")
        table.add_column("Status", justify="center")

        leaders = {nid for nid, n in sim.nodes.items() if n.state == "leader"}
        for node_id in sorted(sim.nodes):
            node = sim.nodes[node_id]
            leader_emoji = "👑" if node_id in leaders else " "
            active_emoji = "🟢" if node.is_active else "🔴"
            table.add_row(
                f"{leader_emoji}{node_id}",
                node.state.capitalize(),
                str(node.current_term),
                node.voted_for or "-",
                str(len(node.votes_received)),
                active_emoji,
            )
        layout["states"].update(table)

        # Stats
        num_active = sum(1 for n in sim.nodes.values() if n.is_active)
        num_leaders = sum(1 for n in sim.nodes.values() if n.state == "leader")
        num_parts = len(sim._get_partitions())
        stats_table = Table.grid(expand=True, padding=(0, 1))
        stats_table.add_row("Active", str(num_active))
        stats_table.add_row("Leaders", str(num_leaders))
        stats_table.add_row("Partitions", str(num_parts))
        stats_table.add_row("Progress", f"{sim.tick}/{duration}")
        layout["stats"].update(Panel(stats_table, title="Stats"))

        # Events log (last 15)
        log_text = Text(style="green")
        for event in sim.events[-15:]:
            log_text.append_text(f"[dim]t{event['tick']:4}[/dim] {event['msg']}\n")
        layout["events"].update(Panel(log_text, title="Recent Events", height=15))

        return layout

    with Live(
        make_layout(), screen=True, refresh_per_second=1.0 / tick_delay + 1
    ) as live:
        while sim.tick < duration:
            sim.step()
            live.update(make_layout())
            time.sleep(tick_delay)