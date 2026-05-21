from pydantic import BaseModel, Field
from typing import Literal

class LogRecord(BaseModel):
    timestamp: float
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    message: str
    attributes: dict = Field(default_factory=dict)

class SamplingConfig(BaseModel):
    target_rate: float = Field(0.1, ge=0.001, le=1.0)
    strategy: Literal["uniform", "adaptive", "priority", "reservoir"] = "adaptive"
    seed: int = 42