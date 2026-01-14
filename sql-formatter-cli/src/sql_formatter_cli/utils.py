'''Utility functions for post-processing formatted SQL.'''

import re
import sqlglot
from typing import Dict, Any

UPPER_KEYWORDS = [kw for kw in sqlglot.keywords.KEYWORDS.values() if kw.isupper()]
KEYWORD_PATTERN = re.compile(
    r"\b({})\b".format("|".join(re.escape(kw) for kw in UPPER_KEYWORDS))
)


def adjust_keyword_case(sql: str, case: str) -> str:
    """Adjust keyword casing (post-sqlglot)."""
    if case == "upper":
        return sql
    def lower_kw(match: re.Match) -> str:
        return match.group(1).lower()
    return KEYWORD_PATTERN.sub(lower_kw, sql)


def adjust_indent(sql: str, indent: str) -> str:
    """Adjust indentation unit (post-sqlglot)."""
    if indent == "  ":
        return sql

    old_unit = "  "
    old_unit_len = len(old_unit)
    lines = sql.splitlines(keepends=True)
    result = []
    for line in lines:
        stripped = line.lstrip(old_unit)
        leading_count = (len(line) - len(stripped)) // old_unit_len
        new_leading = indent * leading_count
        result.append(new_leading + stripped.lstrip())
    return "".join(result)
