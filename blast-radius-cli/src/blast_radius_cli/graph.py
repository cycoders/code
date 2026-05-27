import networkx as nx

def transitive_closure(g: nx.DiGraph, seeds: set[str], max_depth: int = 4) -> set[str]:
    visited = set()
    for s in seeds:
        for node in nx.bfs_tree(g, s, depth_limit=max_depth):
            visited.add(node)
    return visited