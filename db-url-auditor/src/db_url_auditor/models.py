from pydantic import BaseModel, Field
from typing import Optional, Literal

class Finding(BaseModel):
    code: str
    severity: Literal["low", "medium", "high", "critical"]
    message: str
    remediation: str

class AuditResult(BaseModel):
    url: str
    scheme: str
    findings: list[Finding] = Field(default_factory=list)
    valid: bool = True