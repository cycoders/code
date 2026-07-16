from pydantic import BaseModel, Field
from typing import Literal

class LatencyHistogram(BaseModel):
    buckets_ms: list[float] = Field(..., min_length=2)
    counts: list[int] = Field(..., min_length=2)

class TimeoutRecommendation(BaseModel):
    p99_ms: float
    p999_ms: float
    recommended_timeout_ms: float
    confidence: Literal["high", "medium", "low"]
    slo_compliant: bool