from typing import Optional
from pydantic import BaseModel


class AuditResult(BaseModel):
    """Represents the result of auditing one sitemap URL."""

    url: str
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    size: Optional[int] = None
    content_type: Optional[str] = None
    final_url: Optional[str] = None
    error: Optional[str] = None

    @property
    def is_ok(self) -> bool:
        return self.status_code is not None and 200 <= self.status_code < 400

    @property
    def is_broken(self) -> bool:
        if self.status_code is not None and 400 <= self.status_code < 500:
            return True
        return self.error is not None and '404' in str(self.error).lower()