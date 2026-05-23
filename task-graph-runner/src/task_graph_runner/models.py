from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class Task:
    name: str
    command: str
    deps: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    retries: int = 0

@dataclass
class Graph:
    tasks: Dict[str, Task]
    edges: List[tuple] = field(default_factory=list)