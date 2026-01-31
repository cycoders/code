import pytest
from security_headers_auditor.header_checks import check_security_headers, _check_hsts, _check_csp
from security_headers_auditor.types import HeaderStatus


class TestHeaderChecks:
    def test_missing_header(self):
        checks = check_security_headers({})
        assert checks["strict-transport-security"].status == HeaderStatus.MISSING
        assert checks["strict-transport-security"].score == 0

    def test_hsts_good(self):
        value = "max-age=31536000; includeSubDomains; preload"
        check = _check_hsts(value)
        assert check.score == 10
        assert "Good" in check.reason

    def test_hsts_weak(self):
        value = "max-age=1000"
        check = _check_hsts(value)
        assert check.score == 0
        assert "too low" in check.reason

    def test_x_content_type_good(self):
        checks = check_security_headers({"x-content-type-options": "nosniff"})
        assert checks["x-content-type-options"].score == 10

    def test_csp_unsafe_inline(self):
        value = "default-src 'self'; script-src 'unsafe-inline'"
        check = _check_csp(value)
        assert check.score == 4
        assert "unsafe-inline" in check.reason

    def test_csp_good(self):
        value = "default-src 'self'; script-src 'self' 'sha384-abc123'"
        check = _check_csp(value)
        assert check.score == 8
