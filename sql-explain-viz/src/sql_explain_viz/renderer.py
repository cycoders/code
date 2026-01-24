from typing import Optional
import webbrowser
from pathlib import Path

from rich.tree import Tree
from rich.console import Console
graphviz import Digraph

from .models import PlanNode

console = Console()


def build_rich_tree(node: PlanNode) -> Tree:
    tree = Tree(node.label, guide_style="cyan", style="bold magenta")
    _add_children(node, tree)
    return tree


def _add_children(node: PlanNode, tree: Tree):
    for child in node.children:
        child_tree = tree.add(child.label, guide_style="green")
        _add_children(child, child_tree)


def render_ascii(node: PlanNode, prefix: str = "", is_tail: bool = True) -> str:
    connector = "└── " if is_tail else "├── "
    line = prefix + connector + node.label
    new_prefix = prefix + ("    " if is_tail else "│   ")
    lines = [line]
    for i, child in enumerate(node.children):
        lines.append(render_ascii(child, new_prefix, i == len(node.children) - 1))
    return "\n".join(lines)


def render_mermaid(node: PlanNode) -> str:
    counter = [0]
    defs: list[str] = []
    edges: list[str] = []

    def dfs(n: PlanNode, parent_id: Optional[str] = None):
        my_id = f"N{counter[0]}"
        counter[0] += 1
        label = str(n.label).replace('"', '\\"').replace('<', '&lt;').replace('>', '&gt;')
        defs.append(f"  {my_id}[\"{label}\"]")
        if parent_id:
            edges.append(f"  {parent_id} --> {my_id}")
        for child in n.children:
            dfs(child, my_id)

    dfs(node)
    return "flowchart TD\n" + "\n".join(defs + edges)


def render_svg(node: PlanNode, output_path: str):
    dot = Digraph(format="svg", graph_attr={"rankdir": "TB", "splines": "ortho"})
    counter = [0]

    def dfs(n: PlanNode, parent_id: Optional[str] = None):
        my_id = str(counter[0])
        counter[0] += 1
        dot.node(my_id, label=n.label, shape="box", style="filled", fillcolor="lightblue")
        if parent_id is not None:
            dot.edge(parent_id, my_id)
        for child in n.children:
            dfs(child, my_id)

    dfs(node)
    dot.render(output_path, cleanup=True)