from enum import Enum

from pydantic import BaseModel

from typing import List, Optional
from datetime import datetime


class Status(str, Enum):
    VALID = "valid"
    WARNING = "warning"
    INVALID = "invalid"
    UNKNOWN = "unknown"


class Issue(str, Enum):
    EXPIRED = "expired"
    NOT_YET_VALID = "not_yet_valid"
    SIGNATURE_INVALID = "signature_invalid"
    UNTRUSTED_ISSUER = "untrusted_issuer"
    MISSING_INTERMEDIATE = "missing_intermediate"
    WRONG_PURPOSE = "wrong_purpose"
    PATH_LEN_EXCEEDED = "path_len_exceeded"
    WEAK_KEY = "weak_key"
    SELF_SIGNED_NOT_ROOT = "self_signed_not_root"


class CertValidation(BaseModel):
    subject_cn: str
    issuer_cn: str
    serial: str
    not_before: datetime
    not_after: datetime
    status: Status
    issues: List[Issue] = []
    fingerprint_sha256: str


class ChainReport(BaseModel):
    chain: List[CertValidation]
    overall_status: Status
    summary: str
    num_issues: int