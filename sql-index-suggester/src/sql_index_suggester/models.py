from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class ColumnUsage:
    predicates: Counter[str] = field(default_factory=Counter)  # "table.col"
    sorts: Counter[str] = field(default_factory=Counter)
    groups: Counter[str] = field(default_factory=Counter)


@dataclass
class QueryUsages:
    usages: Dict[str, ColumnUsage] = field(default_factory=dict)  # table -> usage
    query_count: int = 0


@dataclass
class IndexSuggestion:
    table: str
    columns: List[str]
    score: float
    sql: str
    rationale: str
