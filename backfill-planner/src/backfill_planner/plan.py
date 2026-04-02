from typing import List, Dict, Any
from pydantic import BaseModel


class Phase(BaseModel):
    name: str
    description: str
    est_duration_hours: float
    batches: int
    sql_snippet: str
    risks: List[str] = []


class Plan(BaseModel):
    strategy: str
    dialect: str
    total_rows: int
    total_est_time_hours: float
    optimal_batch_size: int
    phases: List[Phase]
    recommendations: List[str]
    risks: List[str]
    risk_score: str  # "LOW", "MEDIUM", "HIGH"

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()
