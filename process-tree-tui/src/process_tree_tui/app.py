from textual.app import App, ComposeResult, on
from textual.config import Backend
from textual.widgets import (
    Tree,
    Header,
    Footer,
    Input,
    Static,
)
from textual.binding import Binding
from textual.events import Mount

from .tree_builder import populate_tree


class ProcessTreeApp(App[None]):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("k", "kill_process", "Kill (SIGTERM)"),
        Binding("j", "select_next", "Next"),
        Binding("↑", "cursor_up", "Up"),
        Binding("↓", "cursor_down", "Down"),
        Binding("enter", "toggle_node", "Toggle"),
        Binding("space", "toggle_node", "Toggle"),
        Binding("/", "focus_search", "Search"),
    ]

    CSS = """
    Screen {
        layout: vertical;
    }
    #search-input {
        background: $primary;
        color: $text;
        border: tall $secondary 80%;
        height: 1;
        dock: top;
    }
    #proc-tree {
        height: 1fr;
        border: round $primary;
    }
    #proc-tree > .tree--cursor {
        background: $accent 80%;
    }
    #stats {
        dock: bottom;
        height: 1;
        background: $background 80%;
        color: $text-muted;
    }
    """

    def __init__(self, refresh_interval: float = 0.5, initial_search: str = "") -> None:
        super().__init__()
        self.refresh_interval = refresh_interval
        self.initial_search = initial_search

    def compose(self) -> ComposeResult:
        yield Header(path="proc-tree", show_clock=True)
        yield Input(
            "Search by name/cmd...",
            id="search-input",
            value=self.initial_search,
        )
        yield Tree("Loading...", id="proc-tree", expand=True)
        yield Static("Ready", id="stats")
        yield Footer()

    def on_mount(self, event: Mount) -> None:
        self.refresh_tree()
        self.set_interval(self.refresh_tree, self.refresh_interval)

    @on(Input.Changed, "#search-input")
    def on_search_changed(self) -> None:
        self.refresh_tree()

    def refresh_tree(self) -> None:
        tree: Tree = self.query_one("#proc-tree")
        search_input: Input = self.query_one("#search-input")
        search_term = search_input.value.strip()
        try:
            populate_tree(tree, search_term)
            stats: Static = self.query_one("#stats")
            stats.update(
                f"Processes: {len(tree.root.children)} | Refresh: {self.refresh_interval}s | q=quit r=refresh k=kill"
            )
        except Exception as e:
            self.notify(f"Refresh error: {e}", severity="error", timeout=3.0)

    def action_refresh(self) -> None:
        self.refresh_tree()
        self.notify("Refreshed", timeout=1)

    def action_focus_search(self) -> None:
        self.query_one("#search-input", Input).focus()

    def action_toggle_node(self) -> None:
        tree: Tree = self.query_one(Tree)
        node = tree.cursor_node
        if node.has_children:
            node.expanded = not node.expanded

    def action_kill_process(self) -> None:
        tree: Tree = self.query_one(Tree)
        node = tree.cursor_node
        if node.id == "root":
            return
        try:
            pid = int(node.id)
            label_parts = node.label.partition(" ")[0:2]
            proc_name = label_parts[1] if label_parts[1] else "?"
            if self.confirm(f"Terminate PID {pid} ({proc_name[:20]})?", button="SIGTERM"):
                import psutil
                p = psutil.Process(pid)
                p.terminate()
                self.notify(f"SIGTERM sent to {pid}", severity="information", timeout=2)
                self.call_later(self.refresh_tree)
        except psutil.NoSuchProcess:
            self.notify("Process vanished", severity="warning")
        except psutil.AccessDenied:
            self.notify("Permission denied", severity="error")
        except ValueError:
            pass  # Invalid PID
        except Exception as e:
            self.notify(f"Kill failed: {e}", severity="error")

    def action_select_next(self) -> None:
        tree: Tree = self.query_one(Tree)
        tree.action_cursor_down()

    def action_cursor_up(self) -> None:
        tree: Tree = self.query_one(Tree)
        tree.action_cursor_up()

    def action_cursor_down(self) -> None:
        tree: Tree = self.query_one(Tree)
        tree.action_cursor_down()