from db_url_auditor.auditor import audit
from db_url_auditor.parser import parse_url

def test_audit_flow():
    r = parse_url("postgresql://host/db")
    audited = audit(r)
    assert audited.valid is True