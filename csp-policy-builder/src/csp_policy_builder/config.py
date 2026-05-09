from pathlib import Path
import yaml
from typing import Optional

from .types import ScanConfig


def load_config(config_path: Path) -> ScanConfig:
    """Load YAML config file."""
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return ScanConfig(**data)


def save_config(config: ScanConfig, path: Path):
    """Save config to YAML."""
    data = config.model_dump(exclude_unset=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
