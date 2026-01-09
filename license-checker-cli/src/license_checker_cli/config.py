import tomllib
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: Path) -> Dict[str, Any]:
    if not config_path.exists():
        return {}
    with open(config_path, "rb") as f:
        return tomllib.load(f)