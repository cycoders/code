import os
from pathlib import Path
from typing import Any, Dict, Optional

import tomllib
from pydantic import BaseModel, Field, validator

from .models import Headers


def load_config(config_path: Path, overrides: Optional[Dict[str, Any]] = None) -> "Config":
    """Load TOML config with CLI/env overrides."""
    cfg = Config()

    if config_path.exists():
        with config_path.open("rb") as f:
            data = tomllib.load(f)
        cfg = Config.model_validate(data.get("default", {}))

    # Apply overrides
    if overrides:
        cfg = cfg.model_copy(update=overrides)

    # Env vars
    if token := os.getenv("RLT_AUTH_TOKEN"):
        cfg.headers["Authorization"] = f"Bearer {token}"

    return cfg


class Config(BaseModel):
    """Runtime configuration."""

    url: str = Field(..., description="Target URL")
    method: str = "GET"
    headers: Headers = Field(default_factory=dict)
    concurrency: int = Field(10, ge=1, le=1000)
    duration: int = Field(60, ge=1)
    timeout: float = 10.0
    max_retries: int = 3
    backoff_factor: float = 2.0

    @validator("headers", pre=True)
    def parse_headers(cls, v):
        if isinstance(v, str):
            return {h.split(":", 1)[0].strip(): h.split(":", 1)[1].strip() for h in v.split("\n")}
        return v
