from dataclasses import dataclass

@dataclass(frozen=True)
class Event:
    ts: int
    pid: str
    raw: dict

@dataclass
class Graph:
    nodes: set[str]
    edges: list[tuple[str, str]]