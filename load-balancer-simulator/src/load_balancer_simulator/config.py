from typing import List
from pydantic import BaseModel, Field, validator


class BackendConfig(BaseModel):
    name: str = Field(..., min_length=1)
    capacity: int = Field(..., ge=1, description="Max concurrent connections")
    service_time_mean: float = Field(..., gt=0, description="Mean service time (s)")
    service_time_std: float = Field(0.0, ge=0, description="Std dev service time (s)")
    failure_rate: float = Field(0.0, ge=0.0, le=1.0)
    weight: int = Field(1, ge=1)


class Config(BaseModel):
    duration: float = Field(60.0, gt=0)
    arrival_rate: float = Field(10.0, gt=0)
    dt: float = Field(0.01, ge=0.001, le=0.1)
    strategy: str = Field("round-robin", regex="^(round-robin|least-connections|weighted-rr|ip-hash|random)$")
    seed: int | None = None
    backends: List[BackendConfig] = Field(..., min_items=1)

    @validator("backends")
    def at_least_one(cls, v):
        if len(v) < 1:
            raise ValueError("At least one backend required")
        return v

    model_config = {'extra': 'forbid'}