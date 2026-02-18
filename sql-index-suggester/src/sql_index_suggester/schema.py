from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List

import sqlglot
from sqlglot.expressions import CreateIndex, CreateTable, Expression


@dataclass
class Schema:
    tables: Dict[str, Dict[str, str]] = field(default_factory=dict)  # table -> col -> type
    primary_keys: Dict[str, List[str]] = field(default_factory=dict)
    indexes: Dict[str, List[List[str]]] = field(default_factory=dict)  # table -> list of [col1, col2...]


def extract_schema(ddl: str, dialect: str) -> Schema:
    """Extract schema info from DDL SQL."""
    schema = Schema()
    dialect_obj = sqlglot.dialects.dialect(dialect)
    for expression in sqlglot.parse(ddl, dialect=dialect_obj):
        _process_expression(expression, schema)
    return schema


def _process_expression(expr: Expression, schema: Schema) -> None:
    if isinstance(expr, CreateTable):
        table_name = expr.name
        schema.tables[table_name] = {}
        schema.primary_keys[table_name] = []
        schema.indexes[table_name] = []
        for col_def in expr.find(sqlglot.expressions.ColumnDef):
            col_name = col_def.name
            type_str = str(col_def.kind or "unknown")
            schema.tables[table_name][col_name] = type_str
        # Primary keys
        for pk in expr.find(sqlglot.expressions.PrimaryKey):
            for col in pk.this.find(sqlglot.expressions.Column):
                schema.primary_keys[table_name].append(col.name)
    elif isinstance(expr, CreateIndex):
        table_ref = expr.args.get("table")
        if table_ref and hasattr(table_ref, "name"):
            table_name = table_ref.name
            cols = [col.name for col in expr.this.find(sqlglot.expressions.Column) if col.name]
            if cols:
                schema.indexes.setdefault(table_name, []).append(cols)
