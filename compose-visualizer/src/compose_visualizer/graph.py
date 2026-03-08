from typing import Dict, List


Graph = Dict[str, List[str]]


def build_graph(services: Dict[str, 'Service']) -> Graph:
    """Build dependency graph from services."""
    return {name: svc.depends_on for name, svc in services.items()}


def find_cycles(graph: Graph) -> List[List[str]]:
    """Find all cycles using DFS. Returns list of cycles."""

    visited = set()
    rec_stack = set()
    cycles = []

    def dfs(node: str, path: List[str]):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                if dfs(neighbor, path):
                    return True
            elif neighbor in rec_stack:
                # Cycle found
                idx = path.index(neighbor)
                cycles.append(path[idx:] + [neighbor])
                return True

        path.pop()
        rec_stack.remove(node)
        return False

    for node in graph:
        if node not in visited:
            dfs(node, [])

    return cycles