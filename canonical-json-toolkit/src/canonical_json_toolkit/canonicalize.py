import json
from typing import Any

def _canonicalize(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _canonicalize(obj[k]) for k in sorted(obj.keys())}
    if isinstance(obj, list):
        return [_canonicalize(v) for v in obj]
    if isinstance(obj, float):
        if obj != obj or abs(obj) == float('inf'):
            raise ValueError("NaN and Infinity not allowed")
        return obj
    return obj

def canonicalize(obj: Any) -> str:
    """Return RFC 8785 canonical JSON string."""
    cleaned = _canonicalize(obj)
    return json.dumps(cleaned, separators=(',', ':'), ensure_ascii=True, sort_keys=False)

def verify(original: Any, candidate: Any) -> bool:
    """Return True if both objects produce identical canonical form."""
    return canonicalize(original) == canonicalize(candidate)