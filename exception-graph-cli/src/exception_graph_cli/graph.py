from __future__ import annotations

import networkx as nx
from pathlib import Path


def build_graph(files: list[Path]) -> nx.DiGraph:
    g = nx.DiGraph()
    for f in files:
        g.add_node(str(f))
    # simplified propagation edges added by real analyzer
    return g