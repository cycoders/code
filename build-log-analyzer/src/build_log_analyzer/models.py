from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Step(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = Field(..., max_length=200)
    duration: Optional[float] = Field(None, ge=0)
    status: str = Field(default="unknown")
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    start_line: Optional[int] = None


class LogSummary(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    filename: str
    total_duration: Optional[float] = None
    steps: List[Step] = Field(default_factory=list)
    total_errors: int = Field(default=0)
    total_warnings: int = Field(default=0)
    parser_used: str = Field(default="generic")