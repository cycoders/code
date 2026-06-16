import json
from typing import Any

def parse_explain(data: str) -> dict[str, Any]:
    """Parse EXPLAIN JSON into normalized plan tree."""
    return json.loads(data)[0]['Plan']