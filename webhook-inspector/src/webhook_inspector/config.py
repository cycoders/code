import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator

import yaml

class EndpointConfig(BaseModel):
    secret: Optional[str] = None
    timeout: int = 300
    path: str = "/"

class StorageConfig(BaseModel):
    dir: Path = Path("~/.local/share/webhook-inspector/logs").expanduser()

class Config(BaseModel):
    endpoints: Dict[str, EndpointConfig] = Field(default_factory=dict)
    storage: StorageConfig = StorageConfig()
    ui_theme: str = "dark"

    @validator("endpoints", pre=True)
    def parse_endpoints(cls, v):
        if isinstance(v, dict):
            return {
                path: EndpointConfig(**data) for path, data in v.items()
            }
        return v

HOME_CONFIG = Path.home() / ".config" / "webhook-inspector" / "config.yaml"

def load_config(path: Optional[Path] = None) -> Config:
    """Load config from file or env or default."""
    paths = [path] if path else []
    if HOME_CONFIG.exists():
        paths.append(HOME_CONFIG)

    cfg_data = {}
    for p in paths:
        if p.exists():
            with open(p) as f:
                cfg_data.update(yaml.safe_load(f) or {})

    # Env var overrides
    for k, v in os.environ.items():
        if k.startswith("WHI_"):
            cfg_data[k.lower()] = v

    return Config(**cfg_data)
