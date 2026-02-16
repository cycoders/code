from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class Metric(BaseModel):
    displayValue: str
    numericValue: float
    score: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class LighthouseResult(BaseModel):
    overall_score: float = Field(..., alias="score")
    metrics: Dict[str, Metric]
    audits: Dict[str, Dict[str, Any]]
    categories: Dict[str, Dict[str, Any]]


class PerfBudget(BaseModel):
    lcp: float = 2.5  # seconds
    inp: float = 200.0  # ms
    cls: float = 0.1
    ttfb: float = 600.0  # ms
    fcp: float = 1.8  # seconds

    class Config:
        extra = "allow"