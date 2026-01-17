import json
from typing import Any, Callable

def parse_value(val_str: str) -> Any:
    """Parse CLI str to JSON-native type."""
    stripped = val_str.strip()
    if not stripped:
        return None
    simple = {"null": None, "true": True, "false": False}
    if stripped in simple:
        return simple[stripped]
    try:
        return json.loads(stripped)
    except (ValueError, json.JSONDecodeError):
        return stripped  # str

def apply_op(left: Any, operator: str, right: Any) -> bool:
    """Safe operator application."""
    ops: dict[str, Callable[[Any, Any], bool]] = {
        "==": lambda l, r: l == r,
        "!=": lambda l, r: l != r,
        ">": lambda l, r: (isinstance(l, (int, float)) and isinstance(r, (int, float)) and l > r),
        "<": lambda l, r: (isinstance(l, (int, float)) and isinstance(r, (int, float)) and l < r),
        ">=": lambda l, r: (isinstance(l, (int, float)) and isinstance(r, (int, float)) and l >= r),
        "<=": lambda l, r: (isinstance(l, (int, float)) and isinstance(r, (int, float)) and l <= r),
        "contains": lambda l, r: isinstance(l, str) and isinstance(r, str) and r in l,
    }
    op_func = ops.get(operator, ops["=='])
    try:
        return op_func(left, right)
    except (TypeError, ValueError):
        return False