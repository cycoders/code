import json
from pathlib import Path
from typing import List

from rich.tree import Tree
from rich import print as rprint
import jinja2
from jinja2 import FileSystemLoader

from .models import DiffNode, DiffResult


TEMPLATES_DIR = Path(__file__).parent / "templates"


loader = jinja2.FileSystemLoader(str(TEMPLATES_DIR))
env = jinja2.Environment(loader=loader)


CHANGE_COLORS = {
    "added": "green",
    "removed": "red",
    "modified": "yellow",
    "unchanged": "white",
}


def print_diff(diffs: DiffResult) -> None:
    tree = Tree("[bold cyan]Proto Schema Diff[/bold cyan]", guide_style="cyan")
    for diff in diffs:
        _add_to_tree(tree, diff)
    rprint(tree)


def _add_to_tree(tree: Tree, node: DiffNode) -> None:
    color = CHANGE_COLORS.get(node.change_type.value, "white")
    label = f"[bold {color}]{node.change_type.value.upper()}[/bold {color}] {node.kind}: {node.path}"
    child_tree = tree.add(label)
    for child in sorted(node.children, key=lambda n: n.path):
        _add_to_tree(child_tree, child)


def render_html(diffs: DiffResult, template: str = "diff.html.jinja") -> str:
    template = env.get_template(template)
    return template.render(diffs=[_serialize_node(d) for d in diffs])


def to_json(diffs: DiffResult, fp: Path) -> None:
    with fp.open("w") as f:
        json.dump(
            [_serialize_node(d) for d in diffs],
            f,
            indent=2,
            default=str,
        )


def _serialize_node(node: DiffNode) -> dict:
    return {
        "path": node.path,
        "kind": node.kind,
        "change_type": node.change_type.value,
        "old_value": node.old_value,
        "new_value": node.new_value,
        "children": [_serialize_node(c) for c in node.children],
    }
