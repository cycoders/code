from typing import Any, Union, List, MutableMapping, MutableSequence

import json

def truncate(text: str, max_len: int = 40) -> str:
    """Truncate text with ellipsis if too long."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def get_summary(data: Any) -> str:
    """Get compact summary for tree labels."""
    if isinstance(data, dict):
        return f"{{...{len(data)} keys}}"
    if isinstance(data, list):
        return f"[{len(data)} items]"
    if isinstance(data, str) and len(data) > 20:
        return f'"{truncate(data, 17)}"'
    return json.dumps(data, default=str)[:40]


def update_json_at_path(
    data: MutableMapping | MutableSequence, path: List[Union[str, int]], value: Any
) -> None:
    """Mutate JSON data at given path. Supports dict/list. Raises on invalid path."""
    current = data
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value


def load_json(path: str | None = None) -> dict | list:
    """Load JSON from file or stdin."""
    import sys
    import json

    if path:
        with open(path, "r") as f:
            return json.load(f)
    raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("No JSON input provided (file or stdin)")
    return json.loads(raw)