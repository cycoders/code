import pytest
from openapi_auditor_cli.rules.design import DesignRules
from openapi_auditor_cli.rules.security import SecurityRules
from openapi_auditor_cli.models import Issue


def test_design_missing_summary():
    spec = {
        "openapi": "3.1.0",
        "info": {"title": "Test", "version": "1.0"},
        "paths": {"/users": {"post": {}}},
    }
    rules = DesignRules()
    issues = rules.check(spec)
    assert any(i.rule_id == "design.missing-summary" for i in issues)


def test_security_no_schemes():
    spec = {
        "openapi": "3.1.0",
        "info": {"title": "Test"},
        "security": [{"apiKey": []}],
    }
    rules = SecurityRules()
    issues = rules.check(spec)
    assert any(i.rule_id == "security.no-schemes" for i in issues)


def test_performance_wildcard():
    spec = {
        "openapi": "3.1.0",
        "info": {"title": "Test"},
        "paths": {"/api/{proxy+}": {"get": {}}},
    }
    from openapi_auditor_cli.rules.performance import PerformanceRules
    rules = PerformanceRules()
    issues = rules.check(spec)
    assert any(i.rule_id == "performance.wildcard-path" for i in issues)
