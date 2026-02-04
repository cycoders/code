from collections import defaultdict, deque
from typing import Dict, List

import sys

from .types import CommitNode


def build_children_graph(commits: Dict[str, CommitNode]) -> Dict[str, List[str]]:
    """Build forward graph: parent -> children."""
    graph = defaultdict(list)
    for sha, node in commits.items():
        for parent_sha in node.parents:
            if parent_sha in commits:
                graph[parent_sha].append(sha)
    return dict(graph)


def topological_sort(commits: Dict[str, CommitNode]) -> List[str]:
    """
    Kahn's algorithm: old -> new topo order (roots first).

    Ensures parents before children for optimal Mermaid layout.
    """
    if not commits:
        return []

    # Indegree: # unresolved parents
    indegree = {sha: len(node.parents) for sha, node in commits.items()}
    children_graph = build_children_graph(commits)

    queue = deque([sha for sha, deg in indegree.items() if deg == 0])
    order: List[str] = []

    while queue:
        current = queue.popleft()
        order.append(current)

        for child in children_graph.get(current, []):
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    if len(order) != len(commits):
        print(
            f"Warning: Incomplete topo sort ({len(order)}/{len(commits)} commits). "
            "Possible disconnected graph.",
            file=sys.stderr,
        )

    return order
