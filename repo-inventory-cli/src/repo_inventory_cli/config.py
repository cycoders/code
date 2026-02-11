import json
import os
from pathlib import Path

CONFIG_DIR = Path(os.path.expanduser("~/.config/repo-inventory-cli"))
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "paths": [
        str(Path(os.path.expanduser("~/src"))),
        str(Path(os.path.expanduser("~/projects"))),
        str(Path(os.path.expanduser("~/code"))),
        ".",
    ],
    "excludes": ["**/.venv/**", "**/node_modules/**", "**/.nox/**", "**/.tox/**"],
}


def load_config() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return DEFAULT_CONFIG
