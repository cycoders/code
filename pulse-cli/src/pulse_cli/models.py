from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, ConfigDict, Field


class CheckResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    timestamp: datetime
    endpoint_name: str
    url: str
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    content_length: Optional[int] = None
    cert_expiry_days: Optional[float] = None
    success: bool = False


class EndpointConfig(BaseModel):
    name: str
    url: HttpUrl
    expected_status: List[int] = Field(default_factory=lambda: [200])
    max_resp_time: float = 500.0
    content_match: Optional[str] = None
    check_cert: bool = True


class PulseConfig(BaseModel):
    endpoints: List[EndpointConfig]