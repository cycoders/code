import sqlglot
from sqlglot import exp
from sqlglot.dialects import Dialect
from pathlib import Path
from typing import Iterator

from .schema import Schema, Table, Column, Index


def parse_schema(sql_file: str, dialect: str) -> Schema:
    """Parse SQL DDL file into Schema model."""
    sql_content = Path(sql_file).read_text(encoding="utf-8")
    schema = Schema(dialect=dialect)

    try:
        expressions: Iterator[exp.Expression] = sqlglot.parse(sql_content, dialect=dialect)
    except Exception as e:
        raise ValueError(f"Failed to parse SQL with dialect '{dialect}': {e}") from e

    for expr in expressions:
        if isinstance(expr, exp.CreateTable):
            table = _parse_create_table(expr)
            schema.tables[table.name] = table
        elif isinstance(expr, exp.CreateIndex):
            _parse_create_index(expr, schema)

    return schema


def _parse_create_table(create_table: exp.CreateTable) -> Table:
    table_name = create_table.name
    table = Table(name=table_name)

    columns_list = create_table.args.get("columns", [])
    for col_def in columns_list:
        if isinstance(col_def, exp.ColumnDef):
            col_name = col_def.name
            col_type = str(col_def.kind.this or col_def.kind).upper()
            col_nullable = not bool(col_def.find(exp.NotNull))
            col_pk = bool(col_def.find(exp.PrimaryKey))
            col_unique = bool(col_def.find(exp.Unique))

            column = Column(
                name=col_name,
                type_=col_type,
                nullable=col_nullable,
                primary_key=col_pk,
                unique=col_unique,
            )
            table.columns[col_name] = column

    return table


def _parse_create_index(create_index: exp.CreateIndex, schema: Schema) -> None:
    try:
        index_name = create_index.name
        table_name = create_index.table or ""
        if not table_name:
            return  # Skip malformed
        if table_name in schema.tables:
            schema.tables[table_name].indexes.append(Index(name=index_name))
    except AttributeError:
        pass  # Graceful skip for unsupported index forms
