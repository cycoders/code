from typing import Dict, Any, NamedTuple

from .schema import Schema, Table


class DiffResult(NamedTuple):
    added_tables: Dict[str, Table]
    removed_tables: Dict[str, Table]
    changed_tables: Dict[str, Dict[str, Any]]


def diff_schemas(old_schema: Schema, new_schema: Schema) -> DiffResult:
    """Compute semantic diff between two schemas."""
    if old_schema.dialect != new_schema.dialect:
        raise ValueError("Schemas must use the same dialect")

    old_tables = old_schema.tables
    new_tables = new_schema.tables

    added_tables = {k: v for k, v in new_tables.items() if k not in old_tables}
    removed_tables = {k: v for k, v in old_tables.items() if k not in new_tables}
    changed_tables = {}

    common_tables = set(old_tables.keys()) & set(new_tables.keys())
    for table_name in common_tables:
        table_changes = _diff_table(old_tables[table_name], new_tables[table_name])
        if table_changes:
            changed_tables[table_name] = table_changes

    return DiffResult(added_tables, removed_tables, changed_tables)


def _diff_table(old_table: Table, new_table: Table) -> Dict[str, Any] | None:
    old_cols = old_table.columns
    new_cols = new_table.columns
    old_idxs = {idx.name for idx in old_table.indexes}
    new_idxs = {idx.name for idx in new_table.indexes}

    added_cols = set(new_cols.keys()) - set(old_cols.keys())
    removed_cols = set(old_cols.keys()) - set(new_cols.keys())
    changed_cols = {}
    for col_name in set(old_cols.keys()) & set(new_cols.keys()):
        if old_cols[col_name] != new_cols[col_name]:
            changed_cols[col_name] = {
                "old": old_cols[col_name],
                "new": new_cols[col_name],
            }

    added_idxs = new_idxs - old_idxs
    removed_idxs = old_idxs - new_idxs

    changes = {
        "added_columns": list(added_cols),
        "removed_columns": list(removed_cols),
        "changed_columns": changed_cols,
        "added_indexes": list(added_idxs),
        "removed_indexes": list(removed_idxs),
    }
    non_empty_changes = {k: v for k, v in changes.items() if v}

    return non_empty_changes if non_empty_changes else None
