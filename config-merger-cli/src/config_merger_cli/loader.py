import json
from pathlib import Path
from typing import Any, Dict

import yaml
import tomlkit


def detect_format(path: str) -> str:
    """Detect config format by file extension."""
    ext = Path(path).suffix.lower()
    if ext in {'.yaml', '.yml'}:
        return 'yaml'
    if ext == '.json':
        return 'json'
    if ext == '.toml':
        return 'toml'
    raise ValueError(f"Unsupported extension '{ext}' in {path!r}. Use .json/.yaml/.yml/.toml")


def load_config(path: str) -> Dict[str, Any]:
    """Load config file to ordered dict."""
    fmt = detect_format(path)
    try:
        with open(path) as f:
            if fmt == 'yaml':
                data = yaml.safe_load(f)
            elif fmt == 'json':
                data = json.load(f)
            elif fmt == 'toml':
                data = tomlkit.parse(f.read()).as_dict()
            else:
                raise ValueError(f"Bug: unhandled {fmt}")
        return data or {}
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {path}")
    except (yaml.YAMLError, json.JSONDecodeError, tomlkit.TomlReadError) as exc:
        raise ValueError(f"Parse error in {path}: {exc}") from exc