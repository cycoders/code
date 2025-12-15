import tomllib
from pathlib import Path
import platformdirs
from typing import Dict, Any


def get_config_dir() -> Path:
    return Path(platformdirs.user_config_dir("snippet-vault"))


def get_config_path() -> Path:
    return get_config_dir() / "config.toml"


def load_config() -> Dict[str, Any]:
    path = get_config_path()
    if path.exists():
        with open(path, "rb") as f:
            return tomllib.load(f)
    return {}


def get_db_path(config: Dict[str, Any]) -> Path:
    db_path = config.get("db_path")
    if db_path:
        return Path(db_path).expanduser()
    return Path(platformdirs.user_data_dir("snippet-vault")) / "snippets.db"
