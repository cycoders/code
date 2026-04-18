from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class MetricEntry(BaseModel):
    timestamp: datetime
    deploy_id: str = Field(..., min_length=1)
    traffic_pct: float = Field(..., ge=0.0, le=100.0)
    error_rate: float = Field(..., ge=0.0, le=1.0)
    latency_p95: Optional[float] = Field(None, ge=0.0)


class DeployMetrics(BaseModel):
    deploy_id: str
    avg_error_rate: float
    std_error_rate: float
    num_entries: int
    first_ts: datetime
    last_ts: datetime


class SimResult(BaseModel):
    strategy_name: str
    steps: List[int]
    risk_pct: float
    p95_max_error: float
    avg_max_error: float