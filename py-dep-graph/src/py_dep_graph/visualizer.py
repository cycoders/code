import sys
from typing import IO

from rich.console import Console
from rich.tree import Tree

from .graph import DepGraph


def print_tree(graph: DepGraph, console: Console) -> None:
    """Print hierarchical dependency tree using Rich."""
    console.print(f"[bold cyan]Dependencies[/]: {graph.num_nodes} modules, {graph.num_edges} edges")
    tree = Tree("graph", style="bold magenta")
    for node in sorted(graph.nodes):
        if node in graph.adj:
            node_tree = tree.add(f"[blue]{node}[/]", expand=False)
            for dep in sorted(graph.adj[node]):
                node_tree.add(f"[green]{dep}[/]")
    console.print(tree)


def to_dot(graph: DepGraph, f: IO[str]) -> None:
    """Write Graphviz DOT representation."""
    f.write("digraph G {\n")
    f.write("  rankdir=LR;\n")
    f.write("  node [shape=box, style=filled, fillcolor=lightblue];\n")
    for node in sorted(graph.nodes):
        f.write(f'  "{node}" [label="{node}"];\n')
    for fr, deps in sorted(graph.adj.items()):
        for to in sorted(deps):
            f.write(f'  "{fr}" -> "{to}";\n')
    f.write("}\n")
