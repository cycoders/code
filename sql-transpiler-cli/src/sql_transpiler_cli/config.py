import tomllib
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load TOML config file."""
    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
        return data.get("tool", {}).get("sql-transpiler-cli", {})
    except (tomllib.TOMLDecodeError, KeyError, FileNotFoundError) as e:
        return {}