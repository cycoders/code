import tomli
from dataclasses import dataclass, asdict
from pathlib import Path
import platformdirs
from typing import Dict, Any


@dataclass
class Config:
    collapse_threshold: int = 2


DEFAULT_CONFIG = Config()


def load_config(config_path: Path) -> Config:
    """Load config from TOML file."""
    if not config_path.exists():
        return DEFAULT_CONFIG
    with open(config_path, "rb") as f:
        data = tomli.load(f)
    cfg_dict = data.get("collapse", {})
    cfg_dict.setdefault("threshold", DEFAULT_CONFIG.collapse_threshold)
    return Config(**cfg_dict)


def get_default_config_path() -> Path:
    """Get platform-appropriate config dir."""
    return Path(platformdirs.user_config_dir("stacktrace-collapser")) / "config.toml"
