import pytest
from pytest_httpx import HTTPXMock

from cors_auditor_cli.cors_tester import CorsTester
from cors_auditor_cli.models import AuditConfig


@pytest.mark.httpx()
def test_simple_cors_pass(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        "GET",
        "https://example.com",
        headers={
            "access-control-allow-origin": "http://localhost:3000",
            "vary": "Origin",
        },
    )

    config = AuditConfig(url="https://example.com", origins=["http://localhost:3000"])
    tester = CorsTester(config)
    report = tester.run()

    assert report.score == 100.0
    assert report.passed


@pytest.mark.httpx()
def test_simple_wildcard_credentials_fail(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        "GET",
        "https://example.com",
        headers={"access-control-allow-origin": "*"},
    )

    config = AuditConfig(
        url="https://example.com",
        origins=["http://localhost:3000"],
        credentials=True,
    )
    tester = CorsTester(config)
    report = tester.run()

    assert report.score < 100
    assert "Wildcard" in " ".join(c.details for c in report.checks)


@pytest.mark.httpx()
def test_preflight_header_missing(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        "OPTIONS",
        "https://example.com",
        headers={
            "access-control-allow-origin": "http://localhost:3000",
            "access-control-allow-methods": "GET,POST",
            "access-control-allow-headers": "content-type",
        },
    )

    config = AuditConfig(
        url="https://example.com",
        origins=["http://localhost:3000"],
        request_headers=["x-custom"],
    )
    tester = CorsTester(config)
    report = tester.run()

    assert any("x-custom" in d for c in report.checks for d in c.details)
    assert not report.passed


@pytest.mark.httpx()
def test_credentials_acac_fail(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        "GET",
        "https://example.com",
        headers={"access-control-allow-origin": "http://localhost:3000"},
    )
    httpx_mock.add_response(
        "OPTIONS",
        "https://example.com",
        headers={"access-control-allow-origin": "http://localhost:3000"},
    )

    config = AuditConfig(
        url="https://example.com",
        origins=["http://localhost:3000"],
        credentials=True,
    )
    tester = CorsTester(config)
    report = tester.run()

    assert "ACAC" in " ".join(d for c in report.checks for d in c.details)


@pytest.mark.httpx()
def test_error_handling(httpx_mock: HTTPXMock):
    httpx_mock.add_response(500)

    config = AuditConfig(url="https://example.com", origins=["http://localhost:3000"])
    tester = CorsTester(config)
    report = tester.run()

    assert report.checks[0].status_code == 500