from __future__ import annotations
from typing import Any, Dict, List, DefaultDict
from collections import defaultdict
import copy
from pathlib import Path

from ruamel.yaml import YAML, CommentedMap, CommentedSeq, YAMLError

yaml = YAML(typ="rt")

class ResolutionError(Exception):
    """Base error for resolution issues."""

class CycleError(ResolutionError):
    """Detected cycle in references."""

    def __init__(self, node_path: List[str]):
        self.node_path = node_path
        super().__init__(f"Cycle detected at path: {' -> '.join(node_path)}")

class DuplicateAnchorError(ResolutionError):
    """Duplicate anchor name."""

    def __init__(self, anchor_name: str):
        super().__init__(f"Duplicate anchor '&{anchor_name}'")

ANCHORS: Dict[str, Any] = {}

class NodeVisitor:
    """Visitor to collect anchors and detect cycles/sharing."""

    def __init__(self):
        self.anchors: Dict[str, int] = {}  # name -> node_id
        self.node_counts: DefaultDict[int, int] = defaultdict(int)
        self.visited: set[int] = set()

    def visit(self, node: Any, path: List[str] = None) -> None:
        path = path or []
        nid = id(node)
        self.node_counts[nid] += 1

        if nid in self.visited:
            return
        self.visited.add(nid)

        if isinstance(node, CommentedMap):
            self._visit_dict(node, path)
        elif isinstance(node, CommentedSeq):
            self._visit_list(node, path)

    def _visit_dict(self, cmap: CommentedMap, path: List[str]) -> None:
        for key, value in cmap.items():
            key_path = path + [f"'{key}'"]
            self.visit(value, key_path)

    def _visit_list(self, cseq: CommentedSeq, path: List[str]) -> None:
        for i, item in enumerate(cseq):
            self.visit(item, path + [f"[{i}]"])

    def collect_anchors(self, node: Any) -> None:
        if hasattr(node, "ca") and node.ca.anchor:
            name = node.ca.anchor.value
            nid = id(node)
            if name in self.anchors:
                raise DuplicateAnchorError(name)
            self.anchors[name] = nid

        if isinstance(node, (CommentedMap, CommentedSeq)):
            children = node.values() if isinstance(node, CommentedMap) else node
            for child in children:
                self.collect_anchors(child)

    def has_cycle(self, node: Any) -> bool:
        nid = id(node)
        if nid in self.visited:
            return True
        self.visited.add(nid)
        # Recurse simplified
        if isinstance(node, CommentedMap):
            for v in node.values():
                if self.has_cycle(v):
                    return True
        elif isinstance(node, CommentedSeq):
            for item in node:
                if self.has_cycle(item):
                    return True
        return False

    def get_sharing_stats(self) -> Dict[str, Any]:
        shared = {
            name: count
            for name, nid in self.anchors.items()
            if self.node_counts[nid] > 1
        }
        total_nodes = len(self.node_counts)
        shared_nodes = sum(1 for c in self.node_counts.values() if c > 1)
        return {
            "shared_anchors": shared,
            "total_anchors": len(self.anchors),
            "shared_nodes": shared_nodes,
            "total_nodes": total_nodes,
            "dedup_ratio": f"{100 * shared_nodes / total_nodes:.1f}%" if total_nodes else "0%",
        }

def validate_yaml(yaml_str: str) -> Any:
    """Load, validate anchors/cycles."""
    try:
        data = yaml.load(yaml_str)
    except YAMLError as e:
        raise ResolutionError(f"Invalid YAML: {e}") from e

    visitor = NodeVisitor()
    visitor.collect_anchors(data)
    visitor.visit(data)

    if visitor.has_cycle(data):
        raise CycleError([])

    return data

def resolve_yaml(data: Any) -> str:
    """Deepcopy to inline shared structures, dump."""
    derefed = copy.deepcopy(data)
    return yaml.dump(derefed)

def get_sharing_stats(yaml_str: str) -> Dict[str, Any]:
    """Compute sharing stats."""
    data = validate_yaml(yaml_str)
    visitor = NodeVisitor()
    visitor.collect_anchors(data)
    visitor.visit(data)
    return visitor.get_sharing_stats()

def _show_stats(yaml_str: str) -> None:
    from rich.table import Table
    from rich.console import Console
    stats = get_sharing_stats(yaml_str)
    console = Console()

    table = Table(title="Anchor Sharing Stats")
    table.add_column("Anchor", style="cyan")
    table.add_column("Uses", justify="right")
    for name, uses in sorted(stats["shared_anchors"].items()):
        table.add_row(name, str(uses))

    summary = Table.grid(expand=True)
    summary.add_row("Total Anchors", str(stats["total_anchors"]))
    summary.add_row("Shared Nodes", str(stats["shared_nodes"]))
    summary.add_row("Dedup Ratio", stats["dedup_ratio"])

    console.print(table)
    console.print(Panel(summary, title="Summary"))