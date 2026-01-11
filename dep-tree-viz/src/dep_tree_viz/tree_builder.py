from typing import Dict, List
from dataclasses import dataclass

@dataclass
class DepNode:
    namever: str
    children: List["DepNode"] = None

    def __post_init__(self) -> None:
        if self.children is None:
            self.children = []


def build_forest(
    roots: List[str],
    graph: Dict[str, List[str]],
    max_depth: int,
) -> List[DepNode]:
    """
    Build forest of DepNodes with memoization (shares subtrees for efficiency).
    """
    memo: Dict[str, DepNode] = {}

    def _build(namever: str, depth: int = 0) -> DepNode | None:
        if depth >= max_depth:
            return None
        if namever in memo:
            return memo[namever]
        children: List[DepNode] = []
        for child_nv in graph.get(namever, []):
            child = _build(child_nv, depth + 1)
            if child:
                children.append(child)
        node = DepNode(namever, children)
        memo[namever] = node
        return node

    forest: List[DepNode] = []
    for root in roots:
        node = _build(root)
        if node:
            forest.append(node)
    return forest