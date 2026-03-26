import pytest
from unittest.mock import patch, Mock
from src.domain_profiler_cli.profilers.whois import get_whois


@patch("whois.whois")
def test_whois_success(mock_whois):
    mock_w = Mock()
    mock_w.registrar = "GoDaddy"
    mock_w.creation_date = "2020-01-01"
    mock_whois.return_value = mock_w
    result = get_whois("example.com", 5.0)
    assert result["whois"]["registrar"] == "GoDaddy"


@patch("whois.whois")
def test_whois_fail(mock_whois):
    mock_whois.side_effect = Exception("Fail")
    result = get_whois("fail.com", 5.0)
    assert "error" in result["whois"]