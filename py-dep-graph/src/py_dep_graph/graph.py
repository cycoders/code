from typing import Dict, List, Set


class DepGraph:
    """Directed graph for module dependencies. Supports cycle detection."""

    def __init__(self):
        self.adj: Dict[str, Set[str]] = {}
        self.nodes: Set[str] = set()

    def add_edge(self, fr: str, to: str) -> None:
        self.nodes.add(fr)
        self.nodes.add(to)
        if fr not in self.adj:
            self.adj[fr] = set()
        self.adj[fr].add(to)

    @property
    def num_nodes(self) -> int:
        return len(self.nodes)

    @property
    def num_edges(self) -> int:
        return sum(len(deps) for deps in self.adj.values())

    def cycles(self) -> List[List[str]]:
        """Find cycles using DFS. Returns list of cycle paths."""
        colors: Dict[str, int] = {}  # 0: white, 1: gray, 2: black
        path: List[str] = []
        cycles: List[List[str]] = []

        def dfs(node: str) -> bool:
            colors[node] = 1
            path.append(node)
            for nei in self.adj.get(node, set()):
                if nei not in colors:
                    if dfs(nei):
                        return True
                elif colors[nei] == 1:
                    start = path.index(nei)
                    cycles.append(path[start : ] + [nei])
                    return True
            path.pop()
            colors[node] = 2
            return False

        for node in self.nodes:
            if node not in colors:
                dfs(node)
        return cycles
