'''Core SQL formatting logic.''' 

import sqlglot
from typing import Dict, Any

from .utils import adjust_keyword_case, adjust_indent


def format_sql(raw_sql: str, config: Dict[str, Any]) -> str:
    """Format SQL string using config."""
    dialect = config["dialect"]
    line_length = config["line_length"]
    normalize = config["normalize"]

    try:
        formatted = sqlglot.format(
            raw_sql,
            dialect=dialect,
            pretty=True,
            line_length=line_length,
            normalize=normalize,
        )
    except sqlglot.errors.ParseError as e:
        msg = str(e).split("\n")[0]  # First line
        raise ValueError(f"Invalid SQL ({dialect}): {msg}") from e

    formatted = adjust_keyword_case(formatted, config["keyword_case"])
    formatted = adjust_indent(formatted, config["indent"])

    return formatted
