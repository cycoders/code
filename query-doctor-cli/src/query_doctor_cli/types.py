from typing import TypedDict, Dict, List, Set

class TableSchema(TypedDict):
    columns: Dict[str, str]
    indexed_columns: Set[str]

class Issue(TypedDict):
    severity: str
    type_: str
    description: str
    suggestion: str