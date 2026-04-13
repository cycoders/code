import os
from pathlib import Path
from textual.app import App, ComposeResult
from textual.binding import BindingsTarget
from textual.containers import Container
from textual.message import Message
from textual.split import Split
from textual.widgets import (
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    Progress,
    Static,
    Tree,
    TreeNode,
)
from textual.worker import Worker
from textual.css.query import Query

from .gitignore import load_gitignore
from .node import DirNode
from .tree_builder import build_tree
from .utils import format_bytes, format_percent
from .views import DeletePreview, SearchUpdated, TreeDataLoaded


class DiskUsageApp(App[None], BindingsTarget):
    CSS = """
        Screen {
            layout: horizontal;
        }

        #header { dock: top; }
        #footer { dock: bottom; }
        #search-container { dock: top; height: 1; background: $background 50; }
        #progress { dock: top; height: 1; }
        #main-container { layout: horizontal; height: 1fr; }
        #tree { width: 1fr; }
        #info { width: 30; border-left: solid $primary; }
        Tree:focus .tree_node--cursor {
            background: $accent 50;
        }
        Tree > .tree_node {
            padding-left: 2;
        }
    """

    BINDINGS = [
        ("f", "focus_search", "Focus search"),
        ("escape", "clear_search", "Clear search"),
        ("d", "delete_preview", "Delete preview"),
        ("ctrl-c", "request_quit", "Quit"),
        ("?", "show_help"),
    ]

    def __init__(self, root_path: Path, use_gitignore: bool = True):
        self.root_path = root_path
        self.use_gitignore = use_gitignore
        self.tree_root: DirNode | None = None
        self.current_node: DirNode | None = None
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header(id="header", show_clock=True)
        with Container(id="search-container"):
            yield Input(
                placeholder="Press f to search...",
                id="search",
            )
        yield Progress(id="progress")
        with Container(id="main-container"):
            yield Tree(id="tree")
            yield Static(id="info")
        yield Footer()

    def on_mount(self) -> None:
        self.scan_directory()

    async def scan_directory(self) -> None:
        progress = self.query_one(Progress)
        progress.clear()
        task_id = progress.add_task("scan", "Scanning...", total=None)

        gitignore = GitIgnoreSpec([])
        if self.use_gitignore:
            gitignore = load_gitignore(self.root_path)

        await self.run_worker(self._build_tree, gitignore, task_id)

    async def _build_tree(self, gitignore: GitIgnoreSpec, task_id: str) -> None:
        self.tree_root = build_tree(self.root_path, gitignore)
        self.call_from_thread(TreeDataLoaded(self.tree_root))

    def on_tree_data_loaded(self, event: TreeDataLoaded) -> None:
        tree: Tree[DirNode] = self.query_one(Tree)
        root_treenode = self._dirnode_to_treenode(event.node)
        tree.root = root_treenode
        tree.cursor = root_treenode
        tree.focus()
        self.set_interval(1.0, self._update_info)

    def _dirnode_to_treenode(self, dnode: DirNode) -> TreeNode[DirNode]:
        pct = format_percent(dnode.size, self.tree_root.size) if self.tree_root else "0%"
        label = f"[bold cyan]{dnode.name}[/] [dim]{format_bytes(dnode.size)}[/] ({pct} | {dnode.num_leaves:,} files)"
        children = sorted(
            dnode.children.values(),
            key=lambda c: c.size,
            reverse=True,
        )
        treenodes = [
            self._dirnode_to_treenode(child) for child in children[:50]
        ]  # limit depth
        return TreeNode(label, treenodes, data=dnode, expanded=len(treenodes) < 10)

    def action_focus_search(self) -> None:
        self.query_one(Input).focus()

    def action_clear_search(self) -> None:
        input_ = self.query_one(Input)
        input_.value = ""
        self.query_one(Tree).filter("")

    def action_delete_preview(self) -> None:
        tree: Tree[DirNode] = self.query_one(Tree)
        if tree.root and tree.cursor_node:
            node = tree.cursor_node.data
            if node.path == self.root_path:
                self.notify("Cannot delete root", severity="warning")
                return
            self.push_screen(DeletePreview(node))

    def watch_tree_cursor_node(self, tree: Tree[DirNode]):
        self.current_node = tree.cursor_node.data if tree.cursor_node else None

    def _update_info(self) -> None:
        info: Static = self.query_one("#info", Static)
        if self.current_node:
            pct = format_percent(self.current_node.size, self.tree_root.size)
            info.update(
                f"[bold]{self.current_node.name}[/]\n"
                f"{format_bytes(self.current_node.size)} ({pct})\n"
                f"{self.current_node.num_leaves:,} files"
            )
        else:
            info.update("No selection")

    def on_input_changed(self, event: Input.Changed) -> None:
        tree: Tree = self.query_one(Tree)
        tree.filter(event.value)

    def action_show_help(self) -> None:
        self.notify("f:search, d:delete, ?:this, q:quit", title="Help")