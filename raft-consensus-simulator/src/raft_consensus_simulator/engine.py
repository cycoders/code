from typing import Dict, List
from .models import Node, NodeState, LogEntry

class RaftEngine:
    """Core deterministic Raft simulation engine."""
    def __init__(self, node_count: int = 5):
        self.nodes: Dict[int, Node] = {i: Node(id=i) for i in range(node_count)}
        self.time = 0

    def step(self) -> None:
        self.time += 1
        # Simplified election trigger for demo
        for node in self.nodes.values():
            if node.state == NodeState.FOLLOWER and self.time % 5 == 0:
                node.state = NodeState.CANDIDATE
                node.current_term += 1

    def apply_log(self, node_id: int, entry: LogEntry) -> None:
        node = self.nodes[node_id]
        node.log.append(entry)
        node.commit_index = len(node.log) - 1