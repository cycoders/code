from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass
class DirNode:
    path: Path
    size: int = 0
    children: Dict[str, "DirNode"] = None
    num_leaves: int = 0

    def __post_init__(self):
        if self.children is None:
            self.children = {}

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def is_file(self) -> bool:
        return not bool(self.children)