from textual.widget import Widget
from textual.containers import VerticalScroll
from textual.widgets import DataTable, Label
from textual.message import Message

from redis_explorer_tui.redis_client import RedisClient


class RefreshSlowlog(Message):
    pass


class SlowlogViewer(VerticalScroll):
    def __init__(self, client: RedisClient):
        self.client = client
        self.table = DataTable(id="slowlog-table")
        super().__init__()

    def compose(self):
        info_label = Label("Top slow commands (refresh F5)", id="slowlog-info")
        yield info_label
        self.table.add_columns("ID", "Duration (μs)", "Time", "Command", "Args")
        self.table.column_widths = [8, 12, 20, 20, 30]
        yield self.table

    async def on_refresh_slowlog(self, msg: RefreshSlowlog):
        await self.load_slowlog()

    async def load_slowlog(self):
        try:
            logs = await self.client.slowlog_get(20)
            self.table.clear()
            for log in reversed(logs):  # newest first
                log_id, duration, time, cmd_list = log[0], log[1], log[2], log[3]
                cmd = cmd_list[0].upper() if cmd_list else "?"
                args = ", ".join(str(a) for a in cmd_list[1:5])  # truncate
                ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time))
                self.table.add_row(str(log_id), str(duration), ts, cmd, args)
        except Exception as e:
            self.notify(f"Slowlog error: {e}", severity="warning")

    async def on_mount(self):
        await self.load_slowlog()
