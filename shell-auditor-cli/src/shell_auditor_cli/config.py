import os
from pathlib import Path
from typing import Dict, Any

import tomli


XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
CONFIG_DIR = Path(XDG_CONFIG_HOME) / "shell-auditor-cli"
CONFIG_PATH = CONFIG_DIR / "config.toml"


def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "rb") as f:
        return tomli.load(f)