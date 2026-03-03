from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field, validator

class CheckResult(BaseModel):
    type: Literal["simple", "preflight"]
    origin: str
    status_code: int
    headers: Dict[str, str]
    passed: bool
    details: List[str]

class TestCase(BaseModel):
    origin: str
    simple_request: CheckResult
    preflight_request: CheckResult

class AuditConfig(BaseModel):
    url: str
    origins: List[str]
    methods: List[str]
    request_headers: List[str]
    credentials: bool
    timeout: float = 10.0

    @validator("url")
    def validate_url(cls, v):
        from urllib.parse import urlparse
        if not urlparse(v).scheme:
            raise ValueError("URL must include scheme (http/https)")
        return v

class AuditReport(BaseModel):
    url: str
    checks: List[CheckResult] = []
    test_cases: List[TestCase] = []
    score: float = 0.0
    passed: bool = False
    warnings: List[str] = []
    recommendations: List[str] = []

    def _compute_summary(self):
        total_checks = len(self.checks)
        passed_checks = sum(1 for c in self.checks if c.passed)
        self.score = (passed_checks / total_checks) * 100 if total_checks else 0
        self.passed = self.score == 100

        # Auto recommendations
        if any("wildcard" in d.lower() for c in self.checks for d in c.details):
            self.recommendations.append("Replace '*' with specific origins for security")
        if any("vary" in d.lower() for c in self.checks for d in c.details):
            self.recommendations.append("Add 'Vary: Origin' header")
        if self.config.credentials and not all(c.headers.get("access-control-allow-credentials") == "true" for c in self.checks):
            self.recommendations.append("Set ACAC=true for credentialed requests")
