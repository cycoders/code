import sqlglot

import sql_erd_cli.models as models


exp = sqlglot.expressions


def parse_schema(sql: str, dialect: str) -> models.Schema:
    schema = models.Schema()
    try:
        expressions = sqlglot.parse(sql, dialect=dialect)
    except Exception as e:
        raise ValueError(f"Parse error ({dialect}): {e}")

    for expression in expressions:
        if isinstance(expression, exp.CreateTable):
            table_name = expression.name
            table = models.Table(table_name)
            column_defs = expression.expressions or []
            for col_def in column_defs:
                if isinstance(col_def, exp.ColumnDef):
                    name = col_def.name
                    dtype = col_def.kind or exp.DataType(this="unknown")
                    type_str = str(dtype.this) if hasattr(dtype, "this") else "unknown"
                    pk = False
                    fkey = None
                    # Check column constraints
                    for cons in getattr(col_def, "expressions", []):
                        if isinstance(cons, exp.PrimaryKey):
                            pk = True
                        elif isinstance(cons, exp.ForeignKey):
                            ref_table = getattr(cons, "table", None)
                            ref_col = getattr(cons, "column", None)
                            if ref_table:
                                ref_str = ref_table.name
                                if ref_col:
                                    ref_str += f". {ref_col.name}"
                                fkey = ref_str
                    table.columns[name] = models.Column(name, type_str, pk, fkey)
            schema.tables[table_name] = table

    return schema