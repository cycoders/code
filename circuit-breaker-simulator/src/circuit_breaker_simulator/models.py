from typing import Literal, List, Dict, Any
from pydantic import BaseModel, Field, validator

class BreakerConfig(BaseModel):
    name: str = Field(..., min_length=1)
    type: Literal["consecutive", "threshold"] = "consecutive"
    consec_threshold: int = Field(5, ge=1)
    failure_threshold: int = Field(20, ge=1)
    window_secs: int = Field(30, ge=1)
    timeout_secs: int = Field(60, ge=1)

    @validator("consec_threshold", pre=True, always=True)
    def validate_consec(cls, v, values):
        if values.get("type") != "consecutive":
            return 0
        return v

    @validator("failure_threshold", pre=True, always=True)
    def validate_failure(cls, v, values):
        if values.get("type") != "threshold":
            return 0
        return v

class SimulationConfig(BaseModel):
    rps: float = Field(10.0, gt=0.0)
    duration_secs: int = Field(60, gt=0)
    error_rate: float = Field(0.1, ge=0.0, le=1.0)
    ramp_duration_secs: float = Field(0.0, ge=0.0)
    breakers: List[BreakerConfig] = Field(default_factory=list)

    @validator("breakers")
    def ensure_at_least_one(cls, v):
        if not v:
            v = [BreakerConfig(name="default", type="consecutive")]
        return v
