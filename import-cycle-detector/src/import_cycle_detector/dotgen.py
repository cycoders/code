import networkx as nx
from typing import List


def generate_dot(G: nx.DiGraph, cycles: List[List[str]]) -> str:
    """
    Generate Graphviz DOT with cycles highlighted (red edges, yellow nodes).
    """
    cycle_edges: set[tuple[str, str]] = set()
    cycle_nodes: set[str] = set()

    for cycle in cycles:
        cycle_nodes.update(cycle)
        for i in range(len(cycle)):
            u = cycle[i]
            v = cycle[(i + 1) % len(cycle)]
            cycle_edges.add((u, v))

    lines = [
        "digraph Imports {",
        '  rankdir=LR;',
        '  ratio=auto;',
        '  node [shape=box, style=filled, fontname="Arial", fontsize=10];',
        '  edge [fontname="Arial", fontsize=9];',
    ]

    # Nodes
    for node in sorted(G.nodes()):
        fillcolor = "yellow" if node in cycle_nodes else "lightblue"
        lines.append(f'  "{node}" [fillcolor="{fillcolor}", width=1.2];')

    # Edges
    for u, v in sorted(G.edges()):
        color = "red" if (u, v) in cycle_edges else "black"
        penwidth = "3" if (u, v) in cycle_edges else "1"
        lines.append(f'  "{u}" -> "{v}" [color="{color}", penwidth={penwidth}];')

    lines.append("}")
    return "\n".join(lines)