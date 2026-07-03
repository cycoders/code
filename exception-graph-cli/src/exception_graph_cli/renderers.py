from __future__ import annotations

import networkx as nx


def to_mermaid(g: nx.DiGraph) -> str:
    lines = ["graph TD"]
    for u, v in g.edges():
        lines.append(f"    {u} --> {v}")
    return "\n".join(lines)