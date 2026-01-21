import os
from pathlib import Path
from typing import Iterable

from rich.progress import Progress
from sqlglot import Dialects, parse
from sqlglot.dialects import Dialect

from .models import Dialect as DialectEnum, Issue
from .rules import RULES


def lint_paths(
    paths: list[Path], dialect_enum: DialectEnum, verbose: bool = False
) -> list[Issue]:
    dialect_map = {
        DialectEnum.POSTGRES: Dialects.POSTGRES,
        DialectEnum.MYSQL: Dialects.MYSQL,
        DialectEnum.SQLITE: Dialects.SQLITE,
    }
    sql_dialect: Dialect = dialect_map[dialect_enum]

    sql_paths: list[Path] = []
    for p in paths:
        if p.is_dir():
            sql_paths.extend(p.rglob("*.sql"))
        elif p.suffix == ".sql":
            sql_paths.append(p)

    all_issues = []
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
        console=console if verbose else None,
    ) as progress:
        task = progress.add_task("Linting migrations...", total=len(sql_paths))
        for sql_path in sql_paths:
            issues = lint_file(str(sql_path), sql_dialect)
            all_issues.extend(issues)
            progress.advance(task)

    return all_issues


def lint_file(file_path: str, dialect: Dialect) -> list[Issue]:
    issues = []
    try:
        with open(file_path, "r") as f:
            sql = f.read()
        asts = parse(sql, dialect=dialect, read=dialect.parse)
        for stmt in asts:
            for rule in RULES:
                rule_issues = rule(stmt, file_path)
                if rule_issues:
                    issues.extend(rule_issues)
    except Exception as e:
        issues.append(
            Issue(
                "parse_error",
                "error",
                f"Failed to parse SQL: {str(e)}",
                file_path,
                0,
                0,
            )
        )
    return issues