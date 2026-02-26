from textual.widget import Widget
from textual.containers import VerticalScroll
from textual.widgets import Label, Static
from textual.message import Message
from textual.timer import Timer
from typing import Dict, Any

from redis_explorer_tui.redis_client import RedisClient


class RefreshDashboard(Message):
    """Refresh dashboard data."""


class Dashboard(VerticalScroll):
    def __init__(self, client: RedisClient):
        self.client = client
        super().__init__()

    def compose(self) -> list:
        self.memory_label = Label("Memory: loading...", id="memory")
        self.keys_label = Label("Keys: loading...", id="keys")
        self.hits_label = Label("Hit Rate: loading...", id="hits")
        self.uptime_label = Label("Uptime: loading...", id="uptime")
        yield self.memory_label
        yield self.keys_label
        yield self.hits_label
        yield self.uptime_label

    async def on_refresh_dashboard(self, _: RefreshDashboard) -> None:
        await self.load_stats()

    async def load_stats(self) -> None:
        try:
            info = await self.client.info()
            mem = info.get("used_memory_human", "N/A")
            keyspace = info.get("db0", "N/A")  # approx
            hits = f"{info.get('keyspace_hits', 0)} / {info.get('keyspace_misses', 0) + info.get('keyspace_hits', 0):,} ({info.get('keyspace_hit_ratio_human', 'N/A')})",
            uptime = f"{info.get('uptime_in_seconds', 0) / 86400:.1f} days"
            self.memory_label.update(f"Memory Used: {mem}")
            self.keys_label.update(f"Keys (db{self.client.db}): {keyspace}")
            self.hits_label.update(f"Hit/Miss: {hits}")
            self.uptime_label.update(f"Uptime: {uptime}")
        except Exception as e:
            self.memory_label.update(f"Error: {str(e)[:100]}")

    async def on_mount(self) -> None:
        await self.load_stats()
        self.set_interval(10.0, self.load_stats)
