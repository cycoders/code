from textual.containers import VerticalScroll
from textual.widgets import DataTable, TextArea, Input, Label
from textual.message import Message
from textual.events import Mount
from textual.worker import await_worker
from typing import List, Dict, Any

from redis_explorer_tui.redis_client import RedisClient


class TableDataUpdated(Message):
    """Table data ready."""

    def __init__(self, data: List[Dict[str, Any]]):
        super().__init__()
        self.data = data


class Refresh(Message):
    """Refresh table."""


class KeySelected(Message):
    """Key selected for view."""

    def __init__(self, key: str):
        super().__init__()
        self.key = key


class KeyBrowser(VerticalScroll):
    def __init__(self, client: RedisClient):
        self.client = client
        self.keys_data: List[Dict[str, Any]] = []
        self.table = DataTable(id="table")
        super().__init__(id="key-browser")

    def compose(self):
        yield Input(placeholder="Search pattern (*, user:*)", id="search")
        self.table.add_columns("Key", "Type", "Size (B)", "TTL")
        self.table.column_widths = [50, 12, 12, 12]
        yield self.table
        self.viewer = TextArea("Select a key to view", id="viewer", read_only=True)
        yield self.viewer

    async def on_mount(self, event: Mount) -> None:
        self.node = event.node
        await self.load_data()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.load_data(event.value)

    @await_worker
    async def load_data(self, pattern: str = "*"):
        self.post_message(Refresh())
        try:
            keys = await self.client.get_keys(pattern)
            data = []
            for key in keys[:300]:
                typ = await self.client.get_key_type(key)
                size = await self.client.memory_usage(key)
                ttl = await self.client.get_ttl(key)
                data.append({"key": key, "type": typ, "size": size, "ttl": ttl or -1})
            self.post_message(TableDataUpdated(data))
        except Exception as e:
            self.notify(f"Error: {e}", severity="error", timeout=3.0)

    def on_table_data_updated(self, msg: TableDataUpdated) -> None:
        self.keys_data = msg.data
        self.table.clear(animate=False)
        for item in self.keys_data:
            ttl_str = "none" if item["ttl"] == -1 else f"{item['ttl']}"
            self.table.add_row(item["key"], item["type"], str(item["size"]), ttl_str)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        index = event.row_index
        if 0 <= index < len(self.keys_data):
            key = self.keys_data[index]["key"]
            self.post_message(KeySelected(key))

    async def on_refresh(self, _):
        search_val = self.query_one(Input).value
        await self.load_data(search_val)

    async def load_value(self, key: str) -> None:
        await self.worker(self._fetch_value(key))

    async def _fetch_value(self, key: str):
        value = await self.client.get_value(key)
        self.viewer.load_text(value)
