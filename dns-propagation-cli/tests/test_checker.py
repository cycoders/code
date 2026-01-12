import pytest
from unittest.mock import patch, MagicMock, Mock
from time import perf_counter

from dns_propagation_cli.checker import query_single, check_propagation
from dns_propagation_cli.models import Status


resolver_mock = {
    "name": "TestResolver",
    "ip": "1.1.1.1",
    "location": "Test",
}


@pytest.fixture
def mock_time():
    with patch("dns_propagation_cli.checker.time.perf_counter") as m:
        m.side_effect = [0.0, 0.05]
        yield m


class TestQuerySingle:
    @patch("dns_propagation_cli.checker.dns.resolver.Resolver")
    def test_match(self, mock_resolver, mock_time):
        mock_instance = Mock()
        mock_instance.resolve.return_value = [Mock(__str__=lambda: "93.184.216.34")]
        mock_resolver.return_value = mock_instance

        result = query_single(resolver_mock, "ex.com", "A", "93.184.216.34", 5.0)

        assert result.status == Status.PROPAGATED
        assert result.response == "93.184.216.34"
        assert result.latency == 50.0
        mock_instance.resolve.assert_called_once()

    @patch("dns_propagation_cli.checker.dns.resolver.Resolver")
    def test_mismatch(self, mock_resolver, mock_time):
        mock_instance = Mock()
        mock_instance.resolve.return_value = [Mock(__str__=lambda: "198.51.100.1")]
        mock_resolver.return_value = mock_instance

        result = query_single(resolver_mock, "ex.com", "A", "93.184.216.34", 5.0)

        assert result.status == Status.PENDING
        assert result.response == "198.51.100.1"

    @patch("dns_propagation_cli.checker.dns.resolver.Resolver")
    def test_timeout(self, mock_resolver, mock_time):
        mock_instance = Mock()
        mock_instance.resolve.side_effect = [dns.exception.Timeout]
        mock_resolver.return_value = mock_instance

        result = query_single(resolver_mock, "ex.com", "A", "93.184.216.34", 5.0)

        assert result.status == Status.ERROR
        assert result.error == "Timeout"

    @patch("dns_propagation_cli.checker.dns.resolver.Resolver")
    def test_nxdomain(self, mock_resolver, mock_time):
        from dns.resolver import NXDOMAIN

        mock_instance = Mock()
        mock_instance.resolve.side_effect = [NXDOMAIN]
        mock_resolver.return_value = mock_instance

        result = query_single(resolver_mock, "non.ex", "A", "1.1.1.1", 5.0)

        assert result.status == Status.ERROR
        assert result.error == "NXDOMAIN"

    @patch("dns_propagation_cli.checker.dns.resolver.Resolver")
    def test_generic_error(self, mock_resolver, mock_time):
        mock_instance = Mock()
        mock_instance.resolve.side_effect = [Exception("Test error")]
        mock_resolver.return_value = mock_instance

        result = query_single(resolver_mock, "ex.com", "A", "93.184.216.34", 5.0)

        assert result.status == Status.ERROR
        assert "Test error" in result.error


class TestCheckPropagation:
    def test_basic(self):
        # Minimal test: no exception, sorts correctly
        with patch("dns_propagation_cli.checker.query_single") as mock_query:
            mock_query.return_value = PropagationResult(
                "test", "1.1.1.1", "test", Status.PROPAGATED, "ok", 10.0
            )
            results = check_propagation("ex.com", resolvers=[resolver_mock])
            assert len(results) == 1
            assert results[0].status == Status.PROPAGATED
