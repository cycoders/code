import yaml
from pathlib import Path
from typing import Dict, Any

from .models import Config


def load_config(config_path: Optional[Path]) -> Config:
    if config_path and config_path.exists():
        with config_path.open() as f:
            data = yaml.safe_load(f)
        return Config(**data)
    return Config()


def get_service_alias(service: str, aliases: Dict[str, str]) -> str:
    for pattern, alias in aliases.items():
        if pattern in service or service.startswith(pattern):
            return alias
    # Fallback: shorten
    return service.split("-")[0].lower() if "-" in service else service.lower()