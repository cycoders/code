from __future__ import annotations

from textual.app import App, ComposeResult
from textual.widgets import Tree, DataTable, Header, Footer
from textual.events import TreeNodeSelected
from textual.binding import Binding

from .analyzer import BinaryAnalyzer


class BinaryExplorerApp(App):
    BINDINGS = [
        Binding("tab", "next_panel", "Next Panel"),
        Binding("shift+tab", "prev_panel", "Prev Panel"),
        Binding("q", "request_quit", "Quit"),
    ]
    CSS_PATH = "styles.css"

    def __init__(self, analyzer: BinaryAnalyzer):
        self.analyzer = analyzer
        self.title = f"Binary Explorer TUI [{self.analyzer.format} / {self.analyzer.path}]"
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Tree("Binary Explorer", id="sidebar")
        yield DataTable(id="content")
        yield Footer()

    def on_mount(self) -> None:
        tree: Tree = self.query_one(Tree)
        root = tree.root

        root.add_leaf("Info", id="info")
        root.add_leaf("Dependencies", id="deps")
        root.add_leaf("Sections", id="sections")
        root.add_leaf("Symbols", id="symbols")
        root.add_leaf("Strings", id="strings")

        self._update_content("info")

    def action_next_panel(self) -> None:
        tree: Tree = self.query_one(Tree)
        node = tree.focused
        if node:
            next_sib = node.get_next_leaf(root=node.parent)
            if next_sib:
                tree.focus(next_sib)
                self._update_content(next_sib.id)

    def action_prev_panel(self) -> None:
        tree: Tree = self.query_one(Tree)
        node = tree.focused
        if node:
            prev_sib = node.get_previous_leaf(root=node.parent)
            if prev_sib:
                tree.focus(prev_sib)
                self._update_content(prev_sib.id)

    @TreeNodeSelected.on(Tree)
    def on_tree_node_selected(self, event: TreeNodeSelected) -> None:
        self._update_content(event.node.id)

    def _update_content(self, panel_id: str) -> None:
        table: DataTable = self.query_one(DataTable)
        table.clear(columns=True)

        if panel_id == "info":
            table.add_columns("Property", "Value")
            rows = [
                ("Format", self.analyzer.format),
                ("Architecture", self.analyzer.architecture),
                ("Entry Point", f"0x{self.analyzer.entrypoint:x}"),
                ("File Size", self.analyzer.file_size_human),
            ]
            for row in rows:
                table.add_row(*row)

        elif panel_id == "deps":
            table.add_columns("Library")
            for lib in self.analyzer.libraries:
                table.add_row(lib)

        elif panel_id == "sections":
            table.add_columns("Name", "VA", "Size", "Entropy")
            for sec in self.analyzer.sections[:100]:
                va_str = hex_addr(sec["va"]) if sec["va"] is not None else "N/A"
                entropy_str = f"{sec['entropy']:.2f}"
                if sec["entropy"] > 7.5:
                    entropy_str += " 🔥"
                table.add_row(sec["name"], va_str, sec["size_human"], entropy_str)

        elif panel_id == "symbols":
            table.add_columns("Name", "Value", "Size")
            for row in self.analyzer.symbol_rows[:200]:
                table.add_row(*row)

        elif panel_id == "strings":
            table.add_columns("#", "String")
            for i, s in enumerate(self.analyzer.strings[:100], 1):
                table.add_row(str(i), s)

        table.focus()
