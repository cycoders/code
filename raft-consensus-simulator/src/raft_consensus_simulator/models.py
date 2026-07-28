from enum import Enum
from typing import List, Optional
from pydantic import BaseModel

class NodeState(str, Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

class LogEntry(BaseModel):
    term: int
    command: str

class Node(BaseModel):
    id: int
    state: NodeState = NodeState.FOLLOWER
    current_term: int = 0
    voted_for: Optional[int] = None
    log: List[LogEntry] = []
    commit_index: int = 0