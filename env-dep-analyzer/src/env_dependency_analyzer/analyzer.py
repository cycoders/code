import networkx as nx
from typing import Set, List, Dict, Any


def analyze_graph(G: nx.DiGraph, defined: Set[str]) -> Dict[str, Any]:
    """Analyze graph for cycles and external."""
    external = set(G.nodes()) - defined
    cycles: List[List[str]] = []
    try:
        if G.number_of_nodes() > 0:
            cycles = list(nx.simple_cycles(G))
    except:
        pass  # large graph
    return {
        "external": external,
        "cycles": cycles,
    }


def generate_dot(G: nx.DiGraph, defined: Set[str]) -> str:
    """Generate DOT source."""
    lines = [
        "digraph EnvDeps {",
        "  rankdir=LR;",
        "  node [shape=box, style=filled];"
    ]
    # Nodes
    for node in G.nodes():
        if node in defined:
            lines.append(f'  "{node}" [fillcolor="lightgreen"];')
        else:
            lines.append(f'  "{node}" [fillcolor="lightcoral"];')
    # Edges
    for src, tgt in G.edges():
        lines.append(f'  "{src}" -> "{tgt}";')
    lines.append("}")
    return "\n".join(lines)
