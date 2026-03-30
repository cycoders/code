import asyncio
from textual.app import App, ComposeResult, on
from textual.widgets import DataTable, Static, Header, Footer
from textual.worker import await_worker
from textual.binding import Binding
from .messages import TaskDataUpdated, RefreshRequest
from aio_task_monitor.snapshot import take_snapshot


class MonitorApp(App[None]):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "request_refresh", "Refresh"),
        Binding("f", "cycle_filter", "Cycle Filter"),
    ]

    CSS = """
    DataTable {
        height: 1fr;
        border: solid tall $primary;
    }
    Static.stats {
        dock: top;
        height: 1;
        background: $primary 20%;
        color: $text;
    }
    Static.details {
        dock: bottom;
        height: 1fr;
        background: black;
        color: $text;
        padding: 1;
        max-height: 10;
    }
    """

    def __init__(self):
        super().__init__()
        self.filter_mode: str = "all"
        self.filter_modes = ["all", "running", "done", "cancelled"]
        self.tasks_data: list[dict] = []
        self.selected_task: dict | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static("Initializing...", classes="stats", id="stats")
        yield DataTable(id="tasks-table")
        yield Static(id="details")
        yield Footer()

    def on_mount(self) -> None:
        table: DataTable = self.query_one(DataTable)
        table.add_columns("ID", "Name", "Coro", "Done", "Cancelled", expand=True)
        table.cursor_type = "row"
        self.watch_tasks()

    async def watch_tasks(self) -> None:
        """Background worker to poll snapshots."""
        while True:
            try:
                data = take_snapshot()
                self.post_message(TaskDataUpdated(data))
            except Exception as e:
                self.query_one(Static, id="stats").update(f"Error: {e}")
            await asyncio.sleep(0.5)

    @on(TaskDataUpdated)
    def update_data(self, event: TaskDataUpdated) -> None:
        self.tasks_data = self._apply_filter(event.data["tasks"])
        stats = event.data["stats"]
        self.query_one(Static, id="stats").update(
            f"Tasks: {stats['num_tasks']} | "
            f"Running: {stats['num_running']} | "
            f"Done: {stats['num_done']} | "
            f"Cancelled: {stats['num_cancelled']} | "
            f"Filter: {self.filter_mode.capitalize()}"
        )
        self._update_table()

    def _apply_filter(self, tasks: list[dict]) -> list[dict]:
        if self.filter_mode == "all":
            return tasks
        elif self.filter_mode == "running":
            return [t for t in tasks if not t["done"]]
        elif self.filter_mode == "done":
            return [t for t in tasks if t["done"] and not t["cancelled"]]
        elif self.filter_mode == "cancelled":
            return [t for t in tasks if t["cancelled"]]
        return tasks

    def _update_table(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for task in self.tasks_data:
            table.add_row(
                str(task["task_id"]),
                task["name"],
                task["coro_name"],
                "✓" if task["done"] else " ",
                "✗" if task["cancelled"] else " ",
            )

    async def action_request_refresh(self) -> None:
        self.post_message(RefreshRequest())

    async def action_cycle_filter(self) -> None:
        idx = (self.filter_modes.index(self.filter_mode) + 1) % len(self.filter_modes)
        self.filter_mode = self.filter_modes[idx]
        if self.tasks_data:
            self.post_message(TaskDataUpdated({"tasks": self.tasks_data, "stats": {}}))

    async def action_quit(self) -> None:
        self.exit()

    @on(DataTable.TableRowSelected)
    def on_row_selected(self, event: DataTable.TableRowSelected) -> None:
        idx = event.row_key
        if 0 <= idx < len(self.tasks_data):
            task = self.tasks_data[idx]
            stack = "\n".join(task["stack"]) if task["stack"] else "No stack trace available"
            details = self.query_one(Static, id="details")
            details.update(f"Task {task['task_id']} ({task['name']})\n{stack}")
