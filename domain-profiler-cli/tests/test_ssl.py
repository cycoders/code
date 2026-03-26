import pytest
from unittest.mock import patch, Mock, MagicMock
from src.domain_profiler_cli.profilers.ssl import get_ssl_info


@patch("ssl.create_default_context")
@patch("socket.create_connection")
def test_ssl_success(mock_conn, mock_context):
    mock_sock = Mock()
    mock_ssock = Mock()
    mock_ssock.getpeercert.return_value = b"certdata"
    mock_context.return_value.wrap_socket.return_value = mock_ssock
    mock_conn.return_value = mock_sock

    # Mock cryptography
    mock_cert = Mock()
    mock_cert.subject.get_attributes_for_oid.return_value = [Mock()]
    with patch("cryptography.x509.load_der_x509_certificate") as mock_load:
        mock_load.return_value = mock_cert
        result = get_ssl_info("example.com", 443, 5.0)
    assert "ssl" in result


@patch("socket.create_connection")
def test_ssl_fail(mock_conn):
    mock_conn.side_effect = Exception
    result = get_ssl_info("fail.com", 443, 5.0)
    assert "error" in result["ssl"]