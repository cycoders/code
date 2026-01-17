import os
from pathlib import Path
import tomllib

def get_config_path() -> Path:
    """XDG-compliant config path (~/.config/git-worktree-manager/config.toml)."""
    xdg_config = os.getenv("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    return Path(xdg_config) / "git-worktree-manager" / "config.toml"

def load_config() -> dict:
    """Load TOML config, return nested dict."""
    path = get_config_path()
    if not path.exists():
        return {}
    with open(path, "rb") as f:
        return tomllib.load(f)