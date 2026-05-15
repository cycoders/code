import random

from typing import Set, Optional


class Node:
    """
    Raft node state machine: follower, candidate, leader.
    """

    def __init__(
        self,
        node_id: str,
        cluster_size: int,
        et_min: int = 250,
        et_max: int = 500,
    ):
        self.node_id = node_id
        self.cluster_size = cluster_size
        self.et_min = et_min
        self.et_max = et_max
        self.state: str = "follower"
        self.current_term: int = 0
        self.voted_for: Optional[str] = None
        self.votes_received: Set[str] = set()
        self.election_timeout_counter: int = 0
        self.election_timeout: int = random.randint(et_min, et_max)
        self.heartbeat_counter: int = 0
        self.is_active: bool = True

    def tick(self) -> None:
        """Advance timeout counters and check for elections."""
        self.election_timeout_counter += 1
        if self.state in ("follower", "candidate"):
            if self.election_timeout_counter > self.election_timeout:
                self.become_candidate()
        if self.state == "candidate":
            majority = self.cluster_size // 2 + 1
            if len(self.votes_received) >= majority:
                self.become_leader()

    def handle_msg(self, msg_type: str, from_node, term: int) -> None:
        """
        Handle incoming message (append_entries or request_vote).

        Updates term if higher, steps down if leader.
        """
        if term > self.current_term:
            self.current_term = term
            if self.state == "leader":
                self.state = "follower"
            self.voted_for = None
            self.votes_received.clear()
        if msg_type == "append_entries":
            self.election_timeout_counter = 0
        elif msg_type == "request_vote":
            if (
                self.voted_for is None or self.voted_for == from_node.node_id
            ) and term == self.current_term:
                self.voted_for = from_node.node_id
                from_node.votes_received.add(self.node_id)

    def become_candidate(self) -> None:
        """Increment term, vote self, reset timeout."""
        self.state = "candidate"
        self.current_term += 1
        self.voted_for = self.node_id
        self.votes_received = {self.node_id}
        self.election_timeout_counter = 0
        self.election_timeout = random.randint(self.et_min, self.et_max)

    def become_leader(self) -> None:
        """Become leader, reset counters."""
        self.state = "leader"
        self.election_timeout_counter = 0