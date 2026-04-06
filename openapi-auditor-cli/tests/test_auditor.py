import pytest
from openapi_auditor_cli.auditor import Auditor
from openapi_auditor_cli.models import Issue


def test_no_issues():
    spec = {
        "openapi": "3.1.0",
        "info": {"title": "Test", "version": "1.0.0"},
        "paths": {},
    }
    auditor = Auditor()
    issues = auditor.audit(spec)
    assert len(issues) == 0


def test_missing_title():
    spec = {"openapi": "3.1.0", "info": {"version": "1.0.0"}}
    auditor = Auditor()
    issues = auditor.audit(spec)
    assert len(issues) == 1
    assert issues[0].rule_id == "design.missing-title"
    assert issues[0].severity == "error"


def test_too_many_params():
    spec = {
        "openapi": "3.1.0",
        "info": {"title": "Test", "version": "1.0"},
        "paths": {"/test": {"get": {"parameters": [{}] * 6, "summary": "ok"}}},
    }
    auditor = Auditor()
    issues = auditor.audit(spec)
    assert any(i.rule_id == "design.too-many-params" for i in issues)
