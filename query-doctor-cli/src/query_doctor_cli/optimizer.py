import sqlglot
from sqlglot import expressions as exp
from sqlglot.errors import ParseError
from typing import Dict, List, Set
from pathlib import Path
import typer
from .types import TableSchema, Issue

def parse_schema(schema_content: str, dialect: str) -> Dict[str, TableSchema]:
    """Parse CREATE TABLE/INDEX into table schemas."""
    try:
        expressions = sqlglot.parse(schema_content, dialect=dialect)
    except ParseError as e:
        raise ValueError(f"Schema parse error: {e}")

    tables: Dict[str, TableSchema] = {}
    for expr in expressions:
        if not isinstance(expr, exp.Create):
            continue
        kw = expr.keyword.lower()
        if kw == "table":
            table_name = expr.name
            columns: Dict[str, str] = {}
            indexed_columns: Set[str] = set()
            expressions_list = expr.expressions or []
            for col_def in expressions_list:
                if isinstance(col_def, exp.ColumnDef):
                    col_name = col_def.name
                    kind = col_def.kind.name if col_def.kind else "unknown"
                    columns[col_name] = kind
                    # PRIMARY KEY
                    constraints = col_def.args.get("constraints", [])
                    if any(isinstance(c, exp.PrimaryKey) for c in constraints):
                        indexed_columns.add(col_name)
            tables[table_name] = {"columns": columns, "indexed_columns": indexed_columns}
        elif kw == "index":
            if expr.this and isinstance(expr.this, exp.Table):
                table_name = expr.this.name
                index_cols = [e.this.name for e in (expr.expressions or []) if hasattr(e.this, "name")]
                if table_name not in tables:
                    tables[table_name] = {"columns": {}, "indexed_columns": set()}
                tables[table_name]["indexed_columns"].update(index_cols)
    return tables

def diagnose(tables: Dict[str, TableSchema], query: str, dialect: str) -> List[Issue]:
    """Run performance diagnosis rules."""
    try:
        ast = sqlglot.parse_one(query, dialect=dialect)
    except ParseError as e:
        raise ValueError(f"Query parse error: {e}")

    issues: List[Issue] = []

    # 1. SELECT *
    if any(isinstance(s, exp.Star) for s in ast.selects):
        issues.append({
            "severity": "low",
            "type_": "select_star",
            "description": "SELECT * fetches unnecessary columns",
            "suggestion": "List only required columns to reduce I/O"
        })

    # 2. Cartesian product
    used_tables = {t.name for t in ast.find(exp.Table)}
    joins = ast.find(exp.Join)
    if len(used_tables) > 1 and len(joins) < len(used_tables) - 1:
        issues.append({
            "severity": "high",
            "type_": "cartesian_product",
            "description": f"{len(used_tables)} tables with insufficient JOINs",
            "suggestion": "Use explicit INNER JOIN ... ON for all tables"
        })

    # 3. No LIMIT
    if ast.args.get("limit") is None:
        issues.append({
            "severity": "medium",
            "type_": "no_limit",
            "description": "No LIMIT may scan/fetch entire table",
            "suggestion": "Add LIMIT 100 + OFFSET for pagination/safety"
        })

    # 4. Missing indexes on WHERE filters
    where = ast.args.get("where")
    if where:
        filter_cols = where.find(exp.Column)
        for col_ref in filter_cols:
            table_name = col_ref.table or next(iter(tables), None)
            if not table_name or table_name not in tables:
                continue
            col_name = col_ref.name
            table_schema = tables[table_name]
            if col_name in table_schema["columns"] and col_name not in table_schema["indexed_columns"]:
                issues.append({
                    "severity": "high",
                    "type_": "missing_index_filter",
                    "description": f"WHERE on {table_name}.{col_name} lacks index",
                    "suggestion": f"CREATE INDEX CONCURRENTLY idx_{table_name}_{col_name} ON {table_name}({col_name});"
                })

    # 5. Missing indexes on JOIN keys
    for join in ast.find(exp.Join):
        on = join.args.get("on")
        if on:
            eqs = on.find(exp.EQ)
            for eq in eqs[:2]:  # Limit
                cols_left = eq.left.find(exp.Column)
                cols_right = eq.right.find(exp.Column)
                if cols_left and cols_right:
                    l_table = cols_left[0].table or next(iter(tables))
                    l_col = cols_left[0].name
                    if l_table in tables and l_col in tables[l_table]["columns"] and l_col not in tables[l_table]["indexed_columns"]:
                        issues.append({
                            "severity": "medium",
                            "type_": "missing_index_join",
                            "description": f"JOIN on {l_table}.{l_col} lacks index",
                            "suggestion": f"CREATE INDEX idx_{l_table}_{l_col} ON {l_table}({l_col});"
                        })

    return issues