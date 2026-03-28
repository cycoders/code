from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Union


class ChangeType(Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


@dataclass
class DiffNode:
    path: str
    kind: str  # 'file', 'message', 'enum', 'field', 'service'
    change_type: ChangeType
    old_value: Optional[object] = None
    new_value: Optional[object] = None
    children: List['DiffNode'] = field(default_factory=list)


DiffResult = List[DiffNode]