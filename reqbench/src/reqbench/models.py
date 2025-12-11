from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional, Dict, Any

class BenchmarkConfig(BaseModel):
    url: HttpUrl
    method: str = Field(default="GET", regex="^(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)$")
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    json: Optional[Any] = None
    data: Optional[Any] = None
    clients: List[str] = Field(default_factory=lambda: ["httpx", "requests"])
    concurrency: int = Field(ge=1, le=1000)
    duration: float = Field(ge=1.0, le=300.0)

    @validator("clients")
    def validate_clients(cls, v):
        valid = {"httpx-sync", "httpx", "requests", "aiohttp"}
        invalid = [c for c in v if c not in valid]
        if invalid:
            raise ValueError(f"Invalid clients: {invalid}. Valid: {valid}")
        return v