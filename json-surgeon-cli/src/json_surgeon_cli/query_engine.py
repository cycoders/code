import jmespath

from typing import Any


def apply_jmespath(data: Any, query: str) -> Any:
    """
    Apply JMESPath query to data.

    Raises jmespath.exceptions on error.
    """
    if not query.strip():
        return data
    return jmespath.search(query, data)