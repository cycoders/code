from typing import List

from pydantic import BaseModel, Field, validator


class AnomalyConfig(BaseModel):
    """Configuration for anomaly detection."""

    fields: List[str] = Field(default_factory=list, description="Numeric fields to monitor")
    group_by: List[str] = Field(default_factory=list, description="Columns to group results by")
    threshold: float = Field(3.0, ge=1e-6, description="Outlier threshold")
    method: str = Field("zscore", pattern="^(zscore|iqr|modified_z)$", description="Detection method")

    @validator('fields')
    def fields_required(cls, v):
        if not v:
            raise ValueError('At least one field must be specified')
        return v
