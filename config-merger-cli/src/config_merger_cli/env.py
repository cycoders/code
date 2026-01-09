import os
from typing import Any, Dict


def _parse_value(val: str) -> Any:
    """Coerce env str to native type."""
    val = val.strip().lower()
    if val in ('true', '1', ):
        return True
    if val in ('false', '0', 'null', 'none'):
        return False if 'false' in val or '0' in val else None
    if val.lstrip('-+').replace('.', '', 1).isdigit():
        return int(val) if '.' not in val else float(val)
    return val


def set_nested(config: Dict[str, Any], keys: list[str], value: Any) -> None:
    """Set nested dict leaf: ['service', 'port'] → service.port = value."""
    cur = config
    for key in keys[:-1]:
        if key not in cur:
            cur[key] = {}
        cur = cur[key]
    cur[keys[-1]] = value


def apply_env_overrides(config: Dict[str, Any], prefix: str) -> None:
    """Apply env vars matching prefix, nested via __. Modifies config in-place."""
    for key, val in os.environ.items():
        if key.startswith(prefix):
            path_str = key[len(prefix) : ]
            path = [p for p in path_str.split('__') if p]
            if path:
                set_nested(config, path, _parse_value(val))