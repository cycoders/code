from __future__ import annotations

import sqlglot
from sqlglot.expressions import Select, Column, Where, Order, Group

from .models import ColumnUsage, QueryUsages
from .schema import Schema


def analyze_queries(queries_sql: str, dialect: str, schema: Schema) -> QueryUsages:
    """Analyze all queries for column usages."""
    dialect_obj = sqlglot.dialects.dialect(dialect)
    usages = QueryUsages()
    statements = sqlglot.parse(queries_sql, dialect=dialect_obj)
    for stmt in statements:
        if isinstance(stmt, Select):
            main_table = _get_main_table(stmt)
            if main_table in schema.tables:
                query_usage = _analyze_select(stmt, main_table)
                for col, count in query_usage.predicates.items():
                    usages.usages.setdefault(main_table, ColumnUsage()).predicates.update({col: count})
                # Similar for sorts, groups
                for col, count in query_usage.sorts.items():
                    usages.usages.setdefault(main_table, ColumnUsage()).sorts.update({col: count})
                for col, _ in query_usage.groups.items():
                    usages.usages.setdefault(main_table, ColumnUsage()).groups.update({col: 1})
                usages.query_count += 1
    return usages


def _get_main_table(stmt: Select) -> str:
    if stmt.froms:
        return stmt.froms[0].name or "unknown"
    return "unknown"


def _analyze_select(stmt: Select, main_table: str) -> ColumnUsage:
    usage = ColumnUsage()
    # Predicates
    where = stmt.find(Where)
    if where:
        cols = _collect_columns(where.this)
        for col_str in cols:
            qual_col = _qualify_col(col_str, main_table)
            usage.predicates[qual_col] += 1
    # Sorts
    for order in stmt.args.get("order", []):
        if isinstance(order.this, Column):
            qual_col = _qualify_col(str(order.this), main_table)
            usage.sorts[qual_col] += 1
    # Groups
    for group in stmt.args.get("group", []):
        if isinstance(group.this, Column):
            qual_col = _qualify_col(str(group.this), main_table)
            usage.groups[qual_col] += 1
    return usage


def _collect_columns(exp) -> List[str]:
    cols = []
    if hasattr(exp, "this"):
        if isinstance(exp.this, Column):
            cols.append(str(exp.this))
        elif hasattr(exp.this, "find"):
            cols.extend([str(c) for c in exp.this.find(Column)])
    # Recurse for And/Or
    if hasattr(exp, "args"):
        for arg in exp.args.values():
            if isinstance(arg, list):
                for sub in arg:
                    cols.extend(_collect_columns(sub))
    return list(set(cols))


def _qualify_col(col_str: str, main_table: str) -> str:
    parts = col_str.split(".")
    if len(parts) == 2:
        return col_str
    return f"{main_table}.{parts[-1]}"
