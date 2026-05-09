import pytest
from csp_policy_builder.reporter import strictness_score, audit
from csp_policy_builder.types import Resource


def test_audit_violations():
    res = Resource("https://bad.com", "https", "bad.com", "/", "script-src")
    violations = audit([res], "script-src 'self'")
    assert len(violations) > 0
    assert "bad.com" in violations[0]


def test_no_violations():
    res = Resource("https://self.com", "https", "self.com", "/", "script-src")
    violations = audit([res], "script-src 'self'")
    assert len(violations) == 0
