from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, TabbedContent
from textual.containers import Container

from redis_explorer_tui.redis_client import RedisClient
from redis_explorer_tui.widgets.dashboard import Dashboard
from redis_explorer_tui.widgets.key_browser import KeyBrowser
from redis_explorer_tui.widgets.slowlog_viewer import SlowlogViewer


class KeySelected:
    """Posted when a key is selected."""

    def __init__(self, key: str):
        self.key = key


class RedisExplorerApp(App[Container]):
    CSS = """
    TabbedContent {
        height: 1fr;
    }
    """

    BINDINGS = [
        ("ctrl+q", "request_quit", "Quit"),
        ("f5", "refresh", "Refresh"),
        ("?", "toggle_dark", "Toggle Dark Mode"),
    ]
    TITLE = "Redis Explorer TUI"

    def __init__(self, host: str, port: int, password, db: int, ssl: bool):
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.ssl = ssl
        self.client: Optional[RedisClient] = None
        super().__init__()

    async def on_mount(self) -> None:
        self.client = RedisClient(self.host, self.port, self.password, self.db, self.ssl)
        await self.client.connect()

        content = TabbedContent(initial="keys")
        content.add_tab(KeyBrowser(self.client), "Keys", id="keys")
        content.add_tab(Dashboard(self.client), "Dashboard", id="dashboard")
        content.add_tab(SlowlogViewer(self.client), "Slowlog", id="slowlog")

        await self.mount(content)
        await self.query_one(KeyBrowser).load_data()

    async def on_key_selected(self, event: KeySelected) -> None:
        browser = self.query_one("#keys KeyBrowser")
        viewer = browser.get_child_by_type("TextArea")
        await viewer.load_value(event.key)

    def action_refresh(self) -> None:
        self.query_one(KeyBrowser).post_message("refresh")
        self.query_one(Dashboard).post_message("refresh")
        self.query_one(SlowlogViewer).post_message("refresh")

    async def on_app_session(self) -> None:
        if self.client:
            await self.client.close()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
