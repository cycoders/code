from typing import List, Optional

from sqlglot import exp
from sqlglot.dialects.postgres import PostgresParser

from .models import Issue

RULES = [
    check_no_drop_table,
    check_no_drop_column,
    check_no_drop_constraint,
    check_add_not_null_no_default,
    check_drop_not_null_no_default,
    check_no_concurrent_index,
    check_truncate_table,
]


def check_no_drop_table(stmt: exp.Expression, file_path: str) -> Optional[List[Issue]]:
    if isinstance(stmt, exp.Drop) and stmt.find(exp.Table):
        line = getattr(stmt, "line", 0) or 0
        col = getattr(stmt, "pos", 0) or 0
        return [
            Issue(
                "no_drop_table",
                "error",
                "Dropping tables risks permanent data loss; consider soft-delete or archiving.",
                file_path,
                line,
                col,
            )
        ]
    return None


def check_no_drop_column(stmt: exp.Expression, file_path: str) -> Optional[List[Issue]]:
    drops = stmt.find_all(exp.Drop)
    for drop in drops:
        if drop.args.get("columns"):  # DROP COLUMN
            line = getattr(stmt, "line", 0) or 0
            col = getattr(stmt, "pos", 0) or 0
            return [
                Issue(
                    "no_drop_column",
                    "error",
                    "Dropping columns risks data loss; migrate data first.",
                    file_path,
                    line,
                    col,
                )
            ]
    return None


def check_no_drop_constraint(stmt: exp.Expression, file_path: str) -> Optional[List[Issue]]:
    drops = stmt.find_all(exp.Drop)
    for drop in drops:
        if isinstance(drop.this, (exp.PrimaryKey, exp.ForeignKey, exp.Unique)):
            line = getattr(stmt, "line", 0) or 0
            col = getattr(stmt, "pos", 0) or 0
            return [
                Issue(
                    "no_drop_constraint",
                    "error",
                    "Dropping constraints can lead to data integrity issues.",
                    file_path,
                    line,
                    col,
                )
            ]
    return None


def check_add_not_null_no_default(stmt: exp.Expression, file_path: str) -> Optional[List[Issue]]:
    if isinstance(stmt, exp.Alter):
        adds = stmt.find_all(exp.Add)
        for add in adds:
            col = add.this
            if isinstance(col, exp.Column) and col.find(exp.NotNull) and not col.find(exp.Default):
                line = getattr(stmt, "line", 0) or 0
                col_pos = getattr(stmt, "pos", 0) or 0
                return [
                    Issue(
                        "add_not_null_no_default",
                        "warning",
                        "Adding NOT NULL column without DEFAULT allows NULLs initially.",
                        file_path,
                        line,
                        col_pos,
                    )
                ]
    return None


def check_drop_not_null_no_default(stmt: exp.Expression, file_path: str) -> Optional[List[Issue]]:
    alters = stmt.find_all(exp.AlterColumn)
    for alter in alters:
        if alter.args.get("kind") == "drop_not_null" and not alter.find(exp.Default):
            line = getattr(stmt, "line", 0) or 0
            col_pos = getattr(stmt, "pos", 0) or 0
            return [
                Issue(
                    "drop_not_null_no_default",
                    "error",
                    "Dropping NOT NULL without adding DEFAULT can introduce NULLs unexpectedly.",
                    file_path,
                    line,
                    col_pos,
                )
            ]
    return None


def check_no_concurrent_index(stmt: exp.Expression, file_path: str) -> Optional[List[Issue]]:
    if isinstance(stmt, exp.CreateIndex) and not stmt.args.get("concurrently"):
        line = getattr(stmt, "line", 0) or 0
        col_pos = getattr(stmt, "pos", 0) or 0
        return [
            Issue(
                "no_concurrent_index",
                "warning",
                "CREATE INDEX blocks writes on large tables; use CONCURRENTLY (Postgres).",
                file_path,
                line,
                col_pos,
            )
        ]
    return None


def check_truncate_table(stmt: exp.Expression, file_path: str) -> Optional[List[Issue]]:
    if isinstance(stmt, exp.Truncate):
        line = getattr(stmt, "line", 0) or 0
        col_pos = getattr(stmt, "pos", 0) or 0
        return [
            Issue(
                "truncate_table",
                "warning",
                "TRUNCATE deletes all data irreversibly; use DELETE with WHERE for safety.",
                file_path,
                line,
                col_pos,
            )
        ]
    return None