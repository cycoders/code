import pytest
from unittest.mock import Mock, MagicMock
from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def mock_scan_data():
    """Mock scan response."""
    return {
        "url": "https://example.com/",
        "status_code": 200,
        "headers": {
            "strict-transport-security": "max-age=31536000; includeSubDomains; preload",
            "content-security-policy": "default-src 'self'",
            "x-content-type-options": "nosniff",
        },
        "html": "<html><head></head><body><script>alert(1);</script><script src=\"/app.js\"></script></body></html>",
    }


@pytest.fixture
def mock_webscanner(mocker, mock_scan_data):
    """Mock WebScanner.scan."""
    mock_scanner = Mock()
    mock_scanner.scan.return_value = mock_scan_data
    mocker.patch(
        "security_headers_auditor.scanner.WebScanner",
        return_value=mock_scanner,
    )
