from .models import AuditResult, Finding

def check_credentials(result: AuditResult) -> list[Finding]:
    if "@" in result.url and ":" in result.url.split("@")[0]:
        return [Finding(code="CRED001", severity="high", message="Credentials in URL", remediation="Use environment variables or a secrets manager")]
    return []

def check_tls(result: AuditResult) -> list[Finding]:
    if result.scheme in {"postgresql", "postgres"} and "sslmode=disable" in result.url:
        return [Finding(code="TLS001", severity="critical", message="TLS disabled", remediation="Set sslmode=require or verify-full")]
    return []