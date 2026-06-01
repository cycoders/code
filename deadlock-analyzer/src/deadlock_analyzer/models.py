from dataclasses import dataclass, field
from typing import List

@dataclass
class LockNode:
    name: str
    location: str

@dataclass
class LockEdge:
    from_node: LockNode
    to_node: LockNode
    location: str

@dataclass
class AnalysisResult:
    cycles: List[List[LockNode]] = field(default_factory=list)
    edges: List[LockEdge] = field(default_factory=list)