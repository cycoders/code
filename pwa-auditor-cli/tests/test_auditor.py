import pytest
import responses
from unittest.mock import patch

from pwa_auditor_cli.auditor import PWAAuditor
from pwa_auditor_cli.output import CheckResult


@pytest.fixture
def mock_session():
    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        yield rsps


class TestPWAAuditor:
    def test_https_pass(self):
        auditor = PWAAuditor("https://example.com")
        result = auditor._https_check()
        assert result.passed
        assert result.points_awarded == 20

    def test_https_fail(self):
        auditor = PWAAuditor("http://example.com")
        result = auditor._https_check()
        assert not result.passed
        assert result.points_awarded == 0

    @responses.activate
    def test_manifest_missing(self, mock_session):
        mock_session.get("https://example.com/", body='<html></html>', status=200)
        auditor = PWAAuditor("https://example.com/")
        result = auditor._manifest_check()
        assert not result.passed

    @responses.activate
    def test_manifest_present_invalid_json(self, mock_session):
        mock_session.get("https://example.com/", body='<link rel="manifest" href="/manifest.json">', status=200)
        mock_session.get("https://example.com/manifest.json", body="invalid json", status=200)
        auditor = PWAAuditor("https://example.com/")
        result = auditor._manifest_check()
        assert not result.passed

    @responses.activate
    def test_manifest_schema_valid(self, mock_session):
        mock_session.get("https://example.com/", body='<link rel="manifest" href="/manifest.json">', status=200)
        good_manifest = {
            "name": "Test",
            "short_name": "Test",
            "start_url": "/",
            "display": "standalone",
            "icons": [{"src": "/icon.png", "sizes": "192x192"}],
        }
        mock_session.get("https://example.com/manifest.json", json=good_manifest, status=200)
        auditor = PWAAuditor("https://example.com/")
        auditor._manifest_check()  # Cache
        result = auditor._manifest_schema_check(CheckResult("", True, "", 0, 0))
        assert result.passed
        assert "good icons" in result.details

    @responses.activate
    def test_manifest_schema_invalid(self, mock_session):
        mock_session.get("https://example.com/", body='<link rel="manifest" href="/manifest.json">', status=200)
        bad_manifest = {"name": 123}  # Invalid type
        mock_session.get("https://example.com/manifest.json", json=bad_manifest, status=200)
        auditor = PWAAuditor("https://example.com/")
        auditor._manifest_check()
        result = auditor._manifest_schema_check(CheckResult("", True, "", 0, 0))
        assert not result.passed

    @responses.activate
    def test_service_worker_found(self, mock_session):
        mock_session.get("https://example.com/", status=200)
        mock_session.get("https://example.com/sw.js", status=200, headers={"content-type": "application/javascript"})
        auditor = PWAAuditor("https://example.com/")
        result = auditor._service_worker_check()
        assert result.passed

    @responses.activate
    def test_service_worker_missing(self, mock_session):
        mock_session.get("https://example.com/", status=200)
        mock_session.get("https://example.com/sw.js", status=404)
        auditor = PWAAuditor("https://example.com/")
        result = auditor._service_worker_check()
        assert not result.passed

    @responses.activate
    def test_site_unreachable(self, mock_session):
        mock_session.get("https://example.com/", status=500)
        auditor = PWAAuditor("https://example.com/")
        results = auditor.run_checks()
        assert results[0].name == "Site Reachability"
        assert not results[0].passed
