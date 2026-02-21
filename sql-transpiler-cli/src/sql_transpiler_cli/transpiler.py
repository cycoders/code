from typing import List, Tuple

import sqlglot
from sqlglot import parse_one, transpile
from sqlglot.errors import ParseError, CompileError

from .types import Issue


class SQLTranspiler:
    """
    Core transpiler using sqlglot.

    Handles parsing, transpiling, and validation.
    """

    def __init__(self, from_dialect: str, to_dialect: str) -> None:
        self.from_dialect = from_dialect
        self.to_dialect = to_dialect

    def transpile(self, sql: str) -> Tuple[str, List[Issue]]:
        """
        Transpile SQL string, return (transpiled_sql, issues).

        Issues collected from parse/compile/validate steps.
        """
        issues: List[Issue] = []

        # Parse input
        try:
            ast = parse_one(sql, dialect=self.from_dialect)
        except ParseError as e:
            issues.append(Issue(type="parse_from", message=str(e)))
            return sql, issues

        # Transpile
        try:
            transpiled_list = transpile(ast, read=self.from_dialect, write=self.to_dialect)
            transpiled = "".join(transpiled_list)
        except (CompileError, Exception) as e:  # sqlglot can raise others
            issues.append(Issue(type="compile_to", message=str(e)))
            return sql, issues

        # Validate output
        try:
            parse_one(transpiled, dialect=self.to_dialect)
        except ParseError as e:
            issues.append(Issue(type="parse_to", message=str(e)))

        return transpiled, issues