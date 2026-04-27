from __future__ import annotations
import random
from datetime import datetime
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import (
    Footer,
    Header,
    ListView,
    ListItem,
    Static,
    Input,
    Button,
    DataTable,
    Label,
)
from textual.worker import Worker
from textual.message import Message
from textual.screen import ModalScreen
from textual.clipboard import ClipboardAPI
from git import Repo, Commit
from .models import BlameEntry, BlameData
from .parser import parse_blame_porcelain


class DiffScreen(ModalScreen[str]):
    """Modal for showing diff."""

    def __init__(self, diff: str):
        super().__init__()
        self.diff = diff

    def compose(self) -> ComposeResult:
        yield VerticalScroll(Static(self.diff, id="diff-content"))
        yield Footer([Button("Close", variant="primary")], "diff-footer")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()


class BlameListItem(ListItem):
    def __init__(self, entry: BlameEntry):
        self.entry = entry
        super().__init__(Static(""), id=f"item-{entry.lineno}")

    def render(self) -> Static:
        time_str = self.entry.author_time.strftime("%Y-%m-%d %H:%M")
        color = f"#{random.randint(0x000000, 0xFFFFFF):06x}"
        markup = f"[bold {color}]{{self.entry.author}}[/] · {time_str} | {self.entry.content}"
        return Static(markup)


class BlameApp(App[None]):
    CSS = """
    BlameList {
        height: 1fr;
        background: $panel;
    }
    SearchContainer {
        dock: bottom;
        height: 1;
        background: $background 0;
    }
    DetailPanel {
        width: 40;
        height: 1fr;
        background: $panel 80;
        border: round $primary;
    }
    #search-input {
        dock: left;
        width: 1fr;
        border: none;
    }
    #search-type {
        dock: right;
        width: auto;
    }
    """

    BINDINGS = [
        ("/", "focus_search"),
        ("q", "quit", "Quit"),
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("[", "page_up", "Page up"),
        ("]", "page_down", "Page down"),
        ("g", "go_top", "Top"),
        ("G", "go_bottom", "Bottom"),
        ("enter", "toggle_detail"),
        ("dd", "copy_sha"),
        ("yy", "copy_author"),
    ]

    def __init__(self, file: Path, repo: Repo, entries: BlameData):
        self.file = file
        self.repo = repo
        self.entries = entries
        self.filtered = entries[:]
        self.selected: Optional[BlameEntry] = None
        self.color_map: dict[str, str] = {}
        self._assign_colors()
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            ListView(id="blame-list"),
            Horizontal(
                Static(id="detail-panel"),
                id="detail-container",
            ),
            id="main",
        )
        yield Container(
            Input(placeholder="Search (author/content/commit)...", id="search-input"),
            Label(":", id="search-label"),
            id="search-container",
        )
        yield Footer()

    def on_mount(self) -> None:
        list_view: ListView = self.query_one("#blame-list")
        list_view.extend(BlameListItem(e) for e in self.filtered)
        self._update_detail()

    async def watch_search_input(self, input: Input) -> None:
        query = input.value.lower()
        self.filtered = [
            e for e in self.entries
            if (query in e.author.lower() or
                query in e.content.lower() or
                query in e.commit.lower())
        ]
        self._refresh_list()

    def _assign_colors(self) -> None:
        authors = list({e.author for e in self.entries})
        for author in authors:
            self.color_map[author] = f"#{random.randint(0x11aa88, 0xddffcc):06x}"

    def _refresh_list(self) -> None:
        list_view: ListView = self.query_one(ListView)
        list_view.clear()
        list_view.extend(BlameListItem(e) for e in self.filtered)

    def _update_detail(self) -> None:
        detail: Static = self.query_one("#detail-panel", Static)
        if self.selected:
            c = self.repo.commit(self.selected.commit)
            rel_time = self._relative_time(self.selected.author_time)
            detail.update(f"SHA: {self.selected.commit[:8]} | {c.summary} | {rel_time}")
        else:
            detail.update("Select a line...")

    def _relative_time(self, dt: datetime) -> str:
        now = datetime.now(dt.tzinfo)
        delta = now - dt
        if delta.days < 1:
            return f"{delta.seconds // 3600}h ago"
        return f"{delta.days}d ago"

    def action_cursor_down(self) -> None:
        list_view: ListView = self.query_one(ListView)
        list_view.action_down()
        self._on_select(list_view.index)

    def action_cursor_up(self) -> None:
        list_view: ListView = self.query_one(ListView)
        list_view.action_up()
        self._on_select(list_view.index)

    def _on_select(self, index: int) -> None:
        if 0 <= index < len(self.filtered):
            self.selected = self.filtered[index]
            self._update_detail()

    def action_toggle_detail(self) -> None:
        if not self.selected:
            return
        try:
            prev = self.selected.prev_commit or f"{self.selected.commit}~1"
            diff = self.repo.git.diff(prev, self.selected.commit, "--", self.file, U=5)
            self.push_screen(DiffScreen(diff))
        except Exception:
            self.notify("Diff unavailable", "warning")

    def action_copy_sha(self) -> None:
        if self.selected:
            self.call_later(ClipboardAPI.SetText, self.selected.commit)
            self.notify("SHA copied", "success")

    def action_copy_author(self) -> None:
        if self.selected:
            self.call_later(ClipboardAPI.SetText, self.selected.author)
            self.notify("Author copied", "success")

    def action_focus_search(self) -> None:
        self.query_one(Input).focus()

    def action_go_top(self) -> None:
        self.query_one(ListView).action_page_up(maximum=True)

    def action_go_bottom(self) -> None:
        self.query_one(ListView).action_page_down(maximum=True)