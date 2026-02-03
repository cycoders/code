import pytest
from sitemap_auditor_cli.types import AuditResult


def test_ok_result():
    result = AuditResult(url="https://ex.com/", status_code=200, response_time=0.5)
    assert result.is_ok
    assert not result.is_broken


def test_broken_4xx():
    result = AuditResult(url="https://ex.com/404", status_code=404)
    assert not result.is_ok
    assert result.is_broken


def test_error_with_404():
    result = AuditResult(url="https://ex.com/", error="HTTP 404 Not Found")
    assert result.is_broken


def test_server_error():
    result = AuditResult(url="https://ex.com/", status_code=500)
    assert not result.is_ok
    assert not result.is_broken  # 5xx not 'broken'