import tomllib
from pathlib import Path
import os
from typing import Dict, Any

def merge_configs(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge user config into default."""
    merged = default.copy()
    for key, value in user.items():
        if isinstance(value, dict):
            merged[key] = merge_configs(merged.get(key, {}), value)
        else:
            merged[key] = value
    return merged

def load_config() -> Dict[str, Any]:
    """Load config from ./config.toml or ~/.local-service-hub/config.toml."""
    config_paths = [
        Path.cwd() / "config.toml",
        Path.home() / ".local-service-hub" / "config.toml",
    ]
    config: Dict[str, Any] = {}
    for config_path in config_paths:
        if config_path.exists():
            with open(config_path, "rb") as f:
                user_config = tomllib.load(f)
            config = merge_configs(config, user_config)
    return config

def write_sample_config():
    """Write example config.toml."""
    sample = '''# Example config.toml - override defaults
# All services enabled by default

[services.postgres]
POSTGRES_PASSWORD = "devpass"

[services.redis]
# enabled = true  # default

[services.minio]
MINIO_ROOT_PASSWORD = "minioadmin123"
'''
    config_path = Path.cwd() / "config.toml"
    with open(config_path, "w") as f:
        f.write(sample)
    print(f"Sample config written to {config_path}")
