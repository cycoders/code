from __future__ import annotations

import math
from collections import Counter
from typing import List

from .models import IndexSuggestion, QueryUsages
from .schema import Schema


def generate_suggestions(schema: Schema, usages: QueryUsages, min_score: float = 20.0) -> List[IndexSuggestion]:
    """Generate index suggestions based on usages."""
    suggestions = []
    for table, usage in usages.usages.items():
        if table not in schema.tables:
            continue
        # Skip if PK covers
        pk_cols = set(schema.primary_keys.get(table, []))
        existing_idx = set(tuple(idx[0]) for idx in schema.indexes.get(table, []))  # simplistic
        all_cols = Counter()
        all_cols.update({col.split(".")[-1]: cnt for col, cnt in usage.predicates.items()})
        all_cols.update({col.split(".")[-1]: cnt // 2 for col, cnt in usage.sorts.items()})
        all_cols.update({col.split(".")[-1]: cnt // 3 for col, cnt in usage.groups.items()})
        # Single col
        for col, freq in all_cols.most_common(10):
            if col in pk_cols or col in existing_idx:
                continue
            if col not in schema.tables[table]:
                continue
            score = freq * (usage.predicates.get(f"{table}.{col}", 0) * 3 + 10)
            if score >= min_score:
                sql = f"CREATE INDEX idx_{table}_{col} ON {table} ({col});"
                suggestions.append(IndexSuggestion(table, [col], score, sql, "High freq predicate/sort"))
        # Composites (top 2 co-occur)
        pred_cols = [c.split(".")[-1] for c in usage.predicates]
        pairs = Counter(zip(pred_cols[:-1], pred_cols[1:]))
        for (col1, col2), freq in pairs.most_common(5):
            cols = [col1, col2]
            if any(c in pk_cols for c in cols) or tuple(cols[:1]) in existing_idx:
                continue
            score = freq * 5 + 20
            if score >= min_score:
                sql = f"CREATE INDEX idx_{table}_{col1}_{col2} ON {table} ({col1}, {col2});"
                suggestions.append(IndexSuggestion(table, cols, score, sql, "Common predicate pair"))
    return sorted(suggestions, key=lambda s: s.score, reverse=True)
