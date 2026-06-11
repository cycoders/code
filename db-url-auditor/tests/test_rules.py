from db_url_auditor.models import AuditResult
from db_url_auditor.rules import check_credentials, check_tls

def test_credential_detection():
    r = AuditResult(url="postgres://u:p@host/db", scheme="postgres")
    assert check_credentials(r)[0].code == "CRED001"

def test_tls_disabled():
    r = AuditResult(url="postgresql://host/db?sslmode=disable", scheme="postgresql")
    assert check_tls(r)[0].code == "TLS001"