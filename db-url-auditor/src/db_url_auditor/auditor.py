from .models import AuditResult
from .rules import check_credentials, check_tls

RULES = [check_credentials, check_tls]

def audit(result: AuditResult) -> AuditResult:
    for rule in RULES:
        result.findings.extend(rule(result))
    result.valid = len(result.findings) == 0
    return result