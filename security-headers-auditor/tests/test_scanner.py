import pytest
from unittest.mock import patch, Mock
from security_headers_auditor.scanner import WebScanner


def test_scan_success(mocker):
    mock_resp = Mock()
    mock_resp.url = "https://example.com/"
    mock_resp.status_code = 200
    mock_resp.headers = {"x-content-type-options": "nosniff"}
    mock_resp.text = "<html></html>"
    mock_resp.raise_for_status.return_value = None

    mocker.patch("requests.Session.get", return_value=mock_resp)

    scanner = WebScanner()
    data = scanner.scan("https://test.com", fetch_html=True)
    assert data["status_code"] == 200
    assert "headers" in data


def test_scan_error(mocker):
    mocker.patch("requests.Session.get", side_effect=requests.RequestException("Timeout"))
    scanner = WebScanner()
    with pytest.raises(ValueError, match="Failed to scan"):
        scanner.scan("https://fail.com")
