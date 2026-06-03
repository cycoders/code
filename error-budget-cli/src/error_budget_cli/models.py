from pydantic import BaseModel, Field

class SLO(BaseModel):
    target: float = Field(..., ge=90.0, le=99.999)
    total_requests: int = Field(..., gt=0)
    bad_requests: int = Field(..., ge=0)

class BurnRateWindow(BaseModel):
    window: str
    burn_rate: float
    budget_consumed_pct: float
    projected_exhaustion_hours: float | None