from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class Column:
    name: str
    type_: str
    pk: bool = False
    fkey: Optional[str] = None  # "target_table.target_col"


@dataclass
class Table:
    name: str
    columns: Dict[str, Column] = field(default_factory=dict)


@dataclass
class Schema:
    tables: Dict[str, Table] = field(default_factory=dict)