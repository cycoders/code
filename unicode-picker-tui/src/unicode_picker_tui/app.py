"""Main Textual application."""

import json
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from textual.app import App
from textual.widgets import (
    Header,
    Footer,
    Tree,
    ListView,
    Static,
    SearchInput,
    Label,
)
from textual.containers import Container
from textual.binding import Bindings
from textual.events import Mount

from .data import loader
from .search import search_chars
from .storage import Favorites
from .clipboard import copy
from .widgets import CharItem, CharDetail
from .models import UnicodeChar


class CharPickerApp(App[None], Bindings):
    """Unicode Picker TUI app."""

    CSS = """
    #main {
        layout: horizontal;
        height: 1fr;
    }
    #blocks {
        width: 25%;
        max-width: 30;
    }
    #charlist {
        width: 1fr;
    }
    #detail {
        width: 35%;
        max-width: 50;
    }
    SearchInput {
        dock: top;
        height: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("/", "focus_search", "Search"),
        ("c", "copy_char", "Copy Char"),
        ("C", "copy_codepoint", "Copy Codepoint"),
        ("n", "copy_name", "Copy Name"),
        ("f", "toggle_fav", "Toggle Fav"),
        ("b", "browse_blocks", "Browse Blocks"),
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("?", "show_help", "Help"),
    ]

    chars: List[UnicodeChar] = []
    blocks: Dict[str, List[UnicodeChar]] = {}
    current_block: str = ""
    display_chars: List[UnicodeChar] = []
    query: str = ""
    favs: Favorites

    def __init__(self, title: str, **kwargs):
        super().__init__(title=title, **kwargs)
        self.favs = Favorites(self.storage_path)

    def compose(self):
        yield Header(show_clock=True)
        yield SearchInput(placeholder="Fuzzy search (name)...", id="search")
        with Container(id="main"):
            yield Tree("Unicode Blocks", id="blocks")
            yield ListView(id="charlist")
            yield CharDetail(id="detail")
        yield Footer()

    def on_mount(self) -> None:
        loader.load()
        self.chars = loader.chars
        self.blocks = dict(loader.blocks)
        self.current_block = loader.get_sorted_blocks()[0]
        self.build_ui()

    def build_ui(self) -> None:
        self.build_tree()
        self.update_list()
        self.notify("Ready! 💖 Use / to search, arrows to browse.")

    def build_tree(self) -> None:
        tree: Tree = self.query_one("#blocks", Tree)
        tree.clear()
        for block in loader.get_sorted_blocks():
            label = f"{block} ({len(self.blocks[block])})"
            tree.add_leaf(label, data=block)
        tree.focus_first()

    def update_list(self, chars: List[UnicodeChar] | None = None) -> None:
        listview: ListView = self.query_one("#charlist", ListView)
        listview.clear()
        chars = chars or self.blocks[self.current_block]
        self.display_chars = chars
        for c in chars[:200]:  # Limit for perf
            item = CharItem(CharItem.char, c)
            item.is_fav = self.favs.is_fav(c.codepoint)
            listview.append(item)

    def on_tree_node_selected(self, event: Tree.NodeSelected[str]) -> None:
        self.current_block = event.node.data
        self.query_one("#search").value = ""
        self.update_list()

    def on_search_input_changed(self, event: SearchInput.Changed) -> None:
        self.query = event.value
        if self.query:
            filtered = search_chars(self.chars, self.query)
        else:
            filtered = self.blocks[self.current_block]
        self.update_list(filtered)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        item = event.list_view.highlighted_child
        if isinstance(item, CharItem):
            detail: CharDetail = self.query_one("#detail")
            detail.char = item.char
            detail.is_fav = item.is_fav

    async def action_focus_search(self) -> None:
        self.query_one("#search").focus()

    async def action_copy_char(self) -> None:
        item = self.query_one(ListView).highlighted_child
        if isinstance(item, CharItem) and copy(item.char.char):
            self.notify("Copied char!", title="Clipboard")

    async def action_copy_codepoint(self) -> None:
        item = self.query_one(ListView).highlighted_child
        if isinstance(item, CharItem) and copy(item.char.codepoint):
            self.notify("Copied codepoint!", title="Clipboard")

    async def action_copy_name(self) -> None:
        item = self.query_one(ListView).highlighted_child
        if isinstance(item, CharItem) and copy(item.char.name):
            self.notify("Copied name!", title="Clipboard")

    async def action_toggle_fav(self) -> None:
        item = self.query_one(ListView).highlighted_child
        if isinstance(item, CharItem):
            is_fav = self.favs.toggle(item.char.codepoint)
            item.is_fav = is_fav
            detail: CharDetail = self.query_one("#detail")
            detail.is_fav = is_fav
            self.notify(f"{'Added' if is_fav else 'Removed'} fav ({self.favs.count} total)")

    async def action_browse_blocks(self) -> None:
        self.query_one("#blocks").focus()

    async def action_cursor_down(self) -> None:
        listview = self.query_one(ListView)
        listview.action_cursor_down()

    async def action_cursor_up(self) -> None:
        listview = self.query_one(ListView)
        listview.action_cursor_up()

    async def action_show_help(self) -> None:
        help_text = """
? = Help | / Search | j/k arrows | c/C/n Copy | f Fav | b Blocks | q Quit
        """
        self.notify(help_text.strip(), title="Keys", timeout=5)

    def on_shutdown(self) -> None:
        self.favs.save()
