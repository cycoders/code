from __future__ import annotations
import time
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer, Static, Cell
from textual.binding import Binding
from .monitor import ProcessMonitor
from .utils import value_to_braille, get_intensity_color


class HeatmapApp(App[None]):
    """Main TUI app for process heatmap."""

    CSS_PATH = "app.tcss"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "request_refresh", "Refresh"),
        Binding("escape", "suspend", "Suspend"),
    ]

    def __init__(
        self,
        top: int = 40,
        interval: float = 1.0,
        cpu_thresh: float = 0.0,
    ) -> None:
        super().__init__()
        self.top: int = top
        self.interval: float = max(0.1, interval)
        self.cpu_thresh: float = cpu_thresh
        self.monitor = ProcessMonitor()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(id="stats")
        yield DataTable(id="table")
        yield Footer()

    def on_mount(self) -> None:
        table: DataTable = self.query_one(DataTable)
        table.add_columns("#", "PID", "Name", "CPU", "Mem")
        table.column_widths = [4, 8, 28, 14, 14]
        self.set_interval(self.interval, self.update_display)
        self.update_display()

    def action_request_refresh(self) -> None:
        """Manual refresh binding."""
        self.update_display()

    def update_display(self) -> None:
        """Update table and stats."""
        procs = self.monitor.sample(self.cpu_thresh)[: self.top]
        stats = self.monitor.get_system_stats()
        self.query_one(Static, "#stats").update(
            f"CPU: {stats['cpu_percent']:.1f}% | "
            f"MEM: {stats['mem_percent']:.1f}% ({stats['mem_used_gb']}/{stats['mem_total_gb']} GB) | "
            f"Procs: {len(procs)}"
        )
        table: DataTable = self.query_one(DataTable)
        table.clear(rows=True)
        for i, proc in enumerate(procs):
            cpu = proc["cpu_percent"]
            mem = proc["mem_percent"]
            cpu_braille = value_to_braille(cpu)
            mem_braille = value_to_braille(mem)
            cpu_color = get_intensity_color(cpu)
            mem_color = get_intensity_color(mem)
            cpu_cell = Cell(
                f"{cpu_braille} {cpu:.1f}%",
                styles=f"bold {cpu_color}",
            )
            mem_cell = Cell(
                f"{mem_braille} {mem:.1f}%",
                styles=f"bold {mem_color}",
            )
            table.add_row(
                str(i + 1),
                str(proc["pid"]),
                proc["name"],
                cpu_cell,
                mem_cell,
            )