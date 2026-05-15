import json
import random
from pathlib import Path
from typing import Dict, List, Set, Tuple

from rich.console import Console, ConsoleRenderable
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .node import Node


class Simulator:
    """Core discrete-event simulator for Raft leader election."""

    def __init__(
        self,
        num_nodes: int,
        seed: int,
        heartbeat_interval: int,
        election_timeout_min: int,
        election_timeout_max: int,
        failure_prob: float,
        recovery_prob: float,
        partition_prob: float,
    ):
        random.seed(seed)
        self.num_nodes = num_nodes
        self.cluster_size = num_nodes
        self.heartbeat_interval = heartbeat_interval
        self.et_min = election_timeout_min
        self.et_max = election_timeout_max
        self._failure_prob = failure_prob
        self._recovery_prob = recovery_prob
        self._partition_prob = partition_prob
        self.nodes: Dict[str, Node] = {}
        for i in range(num_nodes):
            node_id = f"node-{i}"
            node = Node(node_id, self.cluster_size, self.et_min, self.et_max)
            self.nodes[node_id] = node
        self.tick: int = 0
        self.events: List[Dict[str, str]] = []
        self.history: List[Dict[str, str]] = []
        self.partitions: List[Set[Node]] = [set(self.nodes.values())]

    def step(self) -> None:
        """One simulation tick: churn -> partitions -> msgs -> handle -> tick -> update partitions."""
        self.tick += 1

        # Churn
        self._inject_churn()

        # Current partitions (active only)
        current_partitions = self._get_partitions()

        # Phase 1: Send msgs within partitions
        msgs: List[Tuple[str, Node, Node, int]] = []
        for part_nodes in current_partitions.values():
            part_active = [n for n in part_nodes if n.is_active]
            if not part_active:
                continue
            # Leaders heartbeat
            leaders = [n for n in part_active if n.state == "leader"]
            for leader in leaders:
                leader.heartbeat_counter += 1
                if leader.heartbeat_counter >= self.heartbeat_interval:
                    leader.heartbeat_counter = 0
                    for follower in part_active:
                        if follower != leader:
                            msgs.append(("append_entries", leader, follower, leader.current_term))
            # Candidates request votes
            candidates = [n for n in part_active if n.state == "candidate"]
            for candidate in candidates:
                for follower in part_active:
                    if follower != candidate:
                        msgs.append(("request_vote", candidate, follower, candidate.current_term))

        # Phase 2: Deliver msgs
        for msg_type, sender, receiver, term in msgs:
            receiver.handle_msg(msg_type, sender, term)

        # Phase 3: Tick nodes
        for part_nodes in current_partitions.values():
            for node in part_nodes:
                if node.is_active:
                    old_state = node.state
                    node.tick()
                    if node.state != old_state:
                        self.events.append(
                            {
                                "tick": str(self.tick),
                                "msg": f"{node.node_id} -> {node.state} (term {node.current_term})",
                            }
                        )

        self.history.append({node_id: node.state for node_id, node in self.nodes.items()})

        # Update partitions
        self._update_partitions()

    def run(self, duration: int) -> None:
        """Run batch simulation."""
        while self.tick < duration:
            self.step()

    def _inject_churn(self) -> None:
        for node in self.nodes.values():
            if node.is_active:
                if random.random() < self._failure_prob:
                    node.is_active = False
                    self.events.append({"tick": str(self.tick), "msg": f"{node.node_id} FAILED"})
            else:
                if random.random() < self._recovery_prob:
                    node.is_active = True
                    node.state = "follower"
                    self.events.append({"tick": str(self.tick), "msg": f"{node.node_id} recovered"})

    def _get_partitions(self) -> Dict[int, Set[Node]]:
        part_dict: Dict[int, Set[Node]] = {}
        for i, part in enumerate(self.partitions):
            active_part = {n for n in part if n.is_active}
            if active_part:
                part_dict[i] = active_part
        return part_dict

    def _update_partitions(self) -> None:
        if random.random() < self._partition_prob and len(self.partitions) < 4:
            # Split largest
            largest = max(self.partitions, key=len, default=set())
            if len(largest) > 1:
                nodes_list = list(largest)
                mid = len(nodes_list) // 2
                p1, p2 = set(nodes_list[:mid]), set(nodes_list[mid:])
                self.partitions = [p for p in self.partitions if p != largest] + [p1, p2]
                self.events.append({"tick": str(self.tick), "msg": "🌐 SPLIT partition"})
        elif random.random() < self._partition_prob / 2 and len(self.partitions) > 1:
            # Merge smallest two
            sorted_parts = sorted(self.partitions, key=len)
            if len(sorted_parts) >= 2:
                merged = sorted_parts[0] | sorted_parts[1]
                self.partitions = (
                    [p for p in self.partitions if p not in (sorted_parts[0], sorted_parts[1])]
                    + [merged]
                )
                self.events.append({"tick": str(self.tick), "msg": "🔗 MERGE partitions"})

    def print_summary(self, console: Console) -> None:
        final_states = self.history[-1]
        leaders = [n for n, s in final_states.items() if s == "leader"]
        num_elections = sum(1 for e in self.events if "-> leader" in e["msg"])
        uptime = {
            n: sum(1 for h in self.history if h.get(n, "") == "leader") / len(self.history)
            for n in self.nodes
        }
        table = Table(title="Summary", box=None)
        table.add_column("Metric")
        table.add_column("Value")
        table.add_row("Final tick", str(self.tick))
        table.add_row("Elections", str(num_elections))
        table.add_row("Final leaders", ", ".join(leaders) or "None")
        table.add_row("Avg leader uptime", f"{sum(uptime.values())/len(uptime):.1%}")
        console.print(table)

    def export(self, path: str) -> None:
        data = {
            "history": self.history,
            "events": self.events,
            "params": {
                "num_nodes": self.num_nodes,
                "tick": self.tick,
            },
        }
        Path(path).write_text(json.dumps(data, indent=2))