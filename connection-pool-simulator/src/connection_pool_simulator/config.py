from typing import Optional, Any

import yaml
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, ValidationError


class SimConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    max_size: int = Field(10, ge=1, description="Maximum pool size")
    acquire_timeout: float = Field(1.0, ge=0.0, description="Acquire timeout in seconds")
    num_clients: int = Field(50, ge=1, description="Number of concurrent clients")
    requests_per_client: int = Field(100, ge=1, description="Requests per client")
    query_duration_mean: float = Field(0.1, ge=0.0, description="Mean query duration (s, Gaussian)")
    query_duration_std: float = Field(0.02, ge=0.0, description="Std dev query duration")
    ramp_up_duration: float = Field(5.0, ge=0.0, description="Ramp-up time for clients (s)")


def get_config(
    config_file: Optional[Path],
    **overrides: Any
) -> SimConfig:
    """Load config from YAML or defaults, apply overrides."""
    overrides = {k: v for k, v in overrides.items() if v is not None}

    if config_file and config_file.exists():
        try:
            with config_file.open("r") as f:
                data = yaml.safe_load(f) or {}
            cfg = SimConfig.model_validate(data)
        except (yaml.YAMLError, ValidationError) as e:
            raise ValueError(f"Invalid config file {config_file}: {e}") from e
    else:
        cfg = SimConfig()

    if overrides:
        cfg = cfg.model_copy(update=overrides)

    return cfg
