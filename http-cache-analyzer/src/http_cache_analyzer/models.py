from typing import Optional, Dict, List, Any
from datetime import datetime

from pydantic import BaseModel, HttpUrl, validator


class CacheDirective(BaseModel):
    name: str
    value: Optional[str] = None


class CachePolicy(BaseModel):
    directives: List[CacheDirective] = []
    max_age: Optional[int] = None
    s_maxage: Optional[int] = None
    expires: Optional[datetime] = None
    etag: Optional[str] = None
    last_modified: Optional[str] = None

    @validator('directives', pre=True)
    def parse_directives(cls, v):
        return v or []


class HttpResponse(BaseModel):
    url: HttpUrl
    status_code: int
    headers: Dict[str, str]
    timestamp: Optional[datetime] = None
    cache_policy: Optional[CachePolicy] = None
