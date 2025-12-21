import networkx as nx
from typing import List


def find_cycles(G: nx.DiGraph) -> List[List[str]]:
    """
    Find all elementary directed cycles using NetworkX.
    """
    try:
        # Generator to list, handles acyclic gracefully
        return list(nx.simple_cycles(G))
    except StopIteration:
        return []
    except nx.NetworkXNoCycle:
        return []