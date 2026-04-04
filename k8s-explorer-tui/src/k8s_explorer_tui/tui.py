'''Textual TUI App for cluster exploration. Data-driven tree + details pane.''' 

from __future__ import annotations
import logging
from typing import Any, Dict

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.message import Message
from textual.widgets import Footer, Header, Static, Tree
from textual.css.query import TreeNodeCSSQuery

import k8s_explorer_tui

logger = logging.getLogger(__name__)


class PodSelected(Message):
    """Event for async pod log loading."""

    def __init__(self, pod_data: Dict[str, Any]):
        super().__init__()
        self.pod_data = pod_data


class ExplorerApp(App):
    """Main TUI App."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]
    CSS = """
        #main {
            height: 100%;
            layout: horizontal;
        }
        #tree {
            width: 50;
            border: round #666;
            padding: 1;
            background: $panel 80%;
        }
        #detail {
            border-left: heavy #666;
            padding: 2;
            background: $panel;
            white-space: pre-wrap;
            overflow-y: scroll;
        }
        Tree:focus {
            border: round #ffff88;
        }
        Tree > .tree_node--expanded > .tree_label {
            text-style: bold;
        }
    """

    def __init__(self, client: k8s_explorer_tui.client.K8sExplorerClient) -> None:
        self.client = client
        super().__init__(title="K8s Explorer TUI v" + k8s_explorer_tui.__version__)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(
            Tree("Loading...", id="tree", expand=True),
            Static(id="detail"),
            id="main",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_tree()

    def action_refresh(self) -> None:
        self.post_message("refresh")

    def action_quit(self) -> None:
        self.exit()

    def on_tree_node_selected(self, event: Tree.NodeSelected[Tree]) -> None:
        node = event.node
        data: Dict[str, Any] = node.data
        if not data:
            return
        node_type = data["type"]
        detail = self.query_one(Static, "#detail")
        match node_type:
            case "cluster":
                detail.update("Kubernetes Cluster\n\nExplore namespaces → deployments/pods.")
            case "namespace":
                ns = data["name"]
                detail.update(f"Namespace: {ns}\n\nSelect deploys/pods for details.")
            case "deployment":
                detail.update(
                    f"Deployment '{data['name']}' ({data['ready']}/{data['desired']})\n"
                    f"in ns '{data['ns']}'"
                )
            case "pod":
                self.post_message(PodSelected(data))

    def on_pod_selected(self, event: PodSelected) -> None:
        self.query_one(Static, "#detail").update("⏳ Loading logs...")
        self.call_later(self._load_pod_logs, event.pod_data)

    def _load_pod_logs(self, pod_data: Dict[str, Any]) -> None:
        ns, name = pod_data["ns"], pod_data["name"]
        try:
            logs = self.client.get_pod_logs(ns, name)
            detail = self.query_one(Static, "#detail")
            detail.update(f"Pod: {name} [{pod_data['status']}] in {ns}\n\n{logs}")
        except Exception as e:
            self.notify(f"Logs failed: {e}", severity="warning", timeout=4.0)
            logger.exception("Log load error")

    def refresh_tree(self) -> None:
        """Async tree refresh."""
        self.call_later(self._populate_tree)

    async def _populate_tree(self) -> None:
        tree: Tree = self.query_one("#tree")
        tree.clear()
        tree.focus()
        root = tree.root
        root.remove_children()

        cluster = root.add("Kubernetes Cluster", data={"type": "cluster"})
        cluster.expand()

        try:
            namespaces = self.client.get_namespaces()
            if not namespaces:
                root.add_leaf("❌ No accessible clusters/namespaces")
                return

            for ns in sorted(namespaces):
                ns_node = cluster.add(
                    f"Namespace: {ns}", data={"type": "namespace", "name": ns}
                )
                ns_node.expand()

                # Deployments
                for dep in self.client.get_deployments_info(ns):
                    label = f"  📦 {dep['name']} ({dep['ready']}/{dep['desired']})"
                    ns_node.add_leaf(label, data={"type": "deployment", **dep, "ns": ns})

                # Pods
                for pod in self.client.get_pods_info(ns):
                    label = (
                        f"  🪨 {pod['name']} [{pod['status']}] "
                        f"(🔄{pod['restarts']})"
                    )
                    ns_node.add_leaf(label, data={"type": "pod", **pod, "ns": ns})

            self.query_one(Static, "#detail").update("Ready! Select a resource.")
        except Exception as e:
            self.notify(str(e), severity="error", timeout=5)
            logger.exception("Tree populate failed")
            root.add_leaf(f"❌ Load failed: {e}")