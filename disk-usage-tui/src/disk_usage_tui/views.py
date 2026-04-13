from textual.screen import ModalScreen
from textual.widgets import DataTable, Label, Button
from textual.message import Message

from .node import DirNode

from .utils import format_bytes

import shutil


class TreeDataLoaded(Message):
    """Emitted when tree is loaded."""
    def __init__(self, node: DirNode):
        super().__init__()
        self.node = node


class SearchUpdated(Message):
    """Emitted on search change."""
    def __init__(self, query: str):
        super().__init__()
        self.query = query


class DeletePreview(ModalScreen[str]):
    """Modal for delete preview."""

    def __init__(self, node: DirNode):
        self.node = node
        self.files = self._get_top_files(node)
        super().__init__()

    def _get_top_files(self, node: DirNode) -> list[DirNode]:
        files: list[DirNode] = []
        def rec(nd: DirNode):
            if not nd.children:
                files.append(nd)
            else:
                for c in nd.children.values():
                    rec(c)
        rec(node)
        files.sort(key=lambda f: f.size, reverse=True)
        return files[:20]

    def compose(self):
        total_files = self.node.num_leaves
        yield Label(
            f"Delete '{self.node.name}'?\n"
            f"Total: {format_bytes(self.node.size)} | Files: {total_files:,}",
            id="delete-title"
        )
        table = DataTable(id="preview-table")
        table.add_columns("File", "Size")
        table.add_rows((f.name, format_bytes(f.size)) for f in self.files)
        yield table
        with self.grid_area("buttons"):
            yield Button("Delete", id="delete", variant="error")
            yield Button("Cancel", id="cancel", variant="primary")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete":
            try:
                shutil.rmtree(self.node.path)
                self.dismiss("deleted")
            except Exception as e:
                self.notify(f"Delete failed: {e}", severity="error")
        else:
            self.dismiss("cancelled")