import pytest
from unittest.mock import patch, Mock
from src.domain_profiler_cli.profilers.dns import get_dns_records


@pytest.fixture
def mock_resolver():
    mock_resolve = Mock()
    mock_resolve.resolve.return_value = [Mock(to_text=lambda: "8.8.8.8")]
    with patch("dns.resolver.Resolver") as mock:
        mock.return_value.resolve = mock_resolve
        yield mock


def test_dns_records(mock_resolver):
    result = get_dns_records("example.com", 5.0)
    assert "dns" in result
    assert "A" in result["dns"]


def test_dns_no_records(mock_resolver):
    mock_resolver.resolve.side_effect = Exception
    result = get_dns_records("fail.com", 5.0)
    assert result["dns"]["error"] == "No records found"