import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from graphql_tester_cli.client import GraphQLClient


@pytest.mark.parametrize("endpoint", ["https://test.com/graphql", "http://localhost:4000"])
def test_client_init(endpoint: str) -> None:
    client = GraphQLClient(endpoint)
    assert client.endpoint == endpoint
    assert client.headers == {}
    assert "wss" in client.ws_endpoint or "ws" in client.ws_endpoint


@patch("gql.Client")
@patch("gql.transport.requests.RequestsHTTPTransport")
def test_execute(mock_transport, mock_client: Mock) -> None:
    mock_transport_instance = Mock()
    mock_transport.return_value = mock_transport_instance
    mock_client_instance = Mock()
    mock_client.return_value = mock_client_instance
    mock_client_instance.execute.return_value = {"data": {"test": True}}

    client = GraphQLClient("https://test.com")
    result = client.execute("{ test }")

    mock_transport.assert_called_once()
    mock_client.assert_called_once()
    mock_client_instance.execute.assert_called_once()
    assert result == {"data": {"test": True}}


@pytest.mark.parametrize("headers", [{"Auth": "token"}, {}])
def test_headers_passed(headers: Dict[str, str]) -> None:
    client = GraphQLClient("https://test.com", headers)
    assert client.headers == headers
