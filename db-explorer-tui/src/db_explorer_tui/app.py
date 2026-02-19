import asyncio
import csv
import time
from pathlib import Path
import databases
from typing import List, Dict, Any

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import DataTable, Footer, Header, Input, Tree, TreeNode
from textual.widget import Widget
from textual import on, work

from db_explorer_tui.db import DBManager


class DBExplorer(App[None]):
    CSS_PATH = "app.tcss"
    BINDINGS = [
        Binding("ctrl-r", "run_query", "Run Query"),
        Binding("ctrl-q", "quit", "Quit"),
        Binding("n", "next_page", "Next Page"),
        Binding("p", "prev_page", "Prev Page"),
        Binding("e", "export_results", "Export CSV"),
        Binding("ctrl-up", "history_up", "History Up"),
        Binding("ctrl-down", "history_down", "History Down"),
    ]

    dsn: str | None = None
    db_manager: DBManager | None = None
    last_results: List[Dict[str, Any]] = []
    page: reactive[int] = 0
    page_size: int = 100
    history: List[str] = []
    history_index: int = -1

    def __init__(self, dsn: str | None = None):
        self.dsn = dsn
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header("💾 DB Explorer TUI", id="header")
        with Horizontal(id="main-container"):
            yield Tree("📋 Schema", id="schema-tree")
            with Vertical(id="content"):
                yield DataTable(
                    id="results-table",
                    show_cursor=True,
                    zebra_stripes=True,
                    expand=True,
                )
                yield Input(
                    placeholder="Enter SQL query (Ctrl+R to run)...",
                    id="query-input",
                    multiline=True,
                )
        yield Footer()

    def on_mount(self) -> None:
        self.query_input = self.query_one("#query-input", Input)
        self.results_table = self.query_one("#results-table", DataTable)
        self.schema_tree = self.query_one("#schema-tree", Tree)
        asyncio.create_task(self._init_db())

    async def _init_db(self) -> None:
        try:
            self.db_manager = DBManager(self.dsn or "sqlite+aiosqlite:///:memory:")
            await self.db_manager.connect()
            await self.load_schema()
            self.notify(f"Connected to {self.db_manager.engine.upper()}", title="Success")
        except Exception as e:
            self.notify(f"Connection failed: {e}", severity="error")
            await asyncio.sleep(2)
            self.exit()

    @work(exclusive=True)
    async def load_schema(self) -> None:
        if not self.db_manager:
            return
        self.schema_tree.clear()
        tables = await self.db_manager.get_tables()
        for table in tables[:50]:  # Limit for large DBs
            node = self.schema_tree.add(
                f"📁 {table}", data=("table", table), expand=False
            )
            columns = await self.db_manager.get_columns(table)
            for col in columns[:20]:
                node.add_leaf(f"  📋 {col}")
        self.schema_tree.focus()

    @on(Tree.HighlightedNodeChanged)
    async def on_tree_highlight_changed(self, event: Tree.HighlightedNodeChanged[TreeNode]):
        node = event.highlighter_tree.highlighted
        if node and node.data and node.data[0] == "table":
            await self.preview_table(node.data[1])

    async def preview_table(self, table: str) -> None:
        query = f'SELECT * FROM "{table}" LIMIT 20'
        self.query_input.value = query
        await self.action_run_query()

    async def action_run_query(self) -> None:
        query = self.query_input.value.strip()
        if not query:
            return
        if not self.db_manager:
            self.notify("No connection", severity="warning")
            return
        try:
            with self.progress.show(f"Executing: {query[:50]}..."):
                self.last_results = await self.db_manager.execute(query)
            self.page = 0
            self.populate_results()
            # History
            if not self.history or self.history[-1] != query:
                self.history.append(query)
            self.history_index = len(self.history) - 1
            self.notify(f"{len(self.last_results)} rows", title="Query OK")
        except Exception as e:
            self.notify(f"Query error: {e}", severity="error")

    def populate_results(self) -> None:
        self.results_table.clear(confirm=False)
        start = self.page * self.page_size
        end = start + self.page_size
        slice_results = self.last_results[start:end]
        if slice_results:
            headers = list(slice_results[0].keys())
            self.results_table.add_columns(*headers)
            for row in slice_results:
                self.results_table.add_row(*[str(row.get(h, "")) for h in headers])
        pages = (len(self.last_results) + self.page_size - 1) // self.page_size
        self.query_one(Header).renderable = Header(
            f"DB Explorer TUI [dim]Page {self.page+1}/{pages} ({len(self.last_results)} rows)[/]",
        )

    async def action_next_page(self) -> None:
        max_page = len(self.last_results) // self.page_size
        if self.page < max_page:
            self.page += 1
            self.populate_results()

    async def action_prev_page(self) -> None:
        if self.page > 0:
            self.page -= 1
            self.populate_results()

    async def action_export_results(self) -> None:
        if not self.last_results:
            self.notify("No results to export", severity="warning")
            return
        ts = int(time.time())
        path = Path.home() / "Downloads" / f"db_export_{ts}.csv"
        path.parent.mkdir(exist_ok=True)
        headers = list(self.last_results[0].keys())
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(self.last_results)
        self.notify(f"Exported {len(self.last_results)} rows to {path}")

    def action_history_up(self) -> None:
        if self.history and self.history_index > 0:
            self.history_index -= 1
            self.query_input.value = self.history[self.history_index]

    def action_history_down(self) -> None:
        if self.history and self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.query_input.value = self.history[self.history_index]

    @on(Input.Changed, "#query-input")
    def on_query_changed(self) -> None:
        self.history_index = -1

    async def on_shutdown(self) -> None:
        if self.db_manager:
            await self.db_manager.close()