from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Column:
    name: str
    type_: str
    nullable: bool = True
    primary_key: bool = False
    unique: bool = False
    default: Optional[str] = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Column):
            return NotImplemented
        return (
            self.name == other.name
            and self.type_ == other.type_
            and self.nullable == other.nullable
            and self.primary_key == other.primary_key
            and self.unique == other.unique
        )


@dataclass
class Index:
    name: str


@dataclass
class Table:
    name: str
    columns: Dict[str, Column] = field(default_factory=dict)
    indexes: List[Index] = field(default_factory=list)


@dataclass
class Schema:
    dialect: str
    tables: Dict[str, Table] = field(default_factory=dict)
