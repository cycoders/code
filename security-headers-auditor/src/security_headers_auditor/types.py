from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel


class HeaderStatus(str, Enum):
    '''Status of a security header check.'''
    MISSING = "missing"
    PRESENT = "present"
    INVALID = "invalid"


class HeaderCheck(BaseModel):
    '''Result of a single header check.'''
    status: HeaderStatus
    score: int  # 0-10
    reason: str
    recommendation: str


class AuditReport(BaseModel):
    '''Full audit report.'''
    url: str
    status_code: int
    grade: str  # A-F
    score: float
    headers: Dict[str, Dict[str, Any]]
