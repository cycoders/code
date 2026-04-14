import pytest
from unittest.mock import patch, MagicMock, ANY
import requests
from src.cert_transparency_cli.ct_client import CTClient

@pytest.fixture
def client():
    return CTClient(timeout=1, retries=1)

@patch("requests.Session.get")
def test_search_success(mock_get, client):
    sample_data = [
        {
            "ID": 541884289,
            "not_before": 1640995200,
            "not_after": 1672531200,
            "issuer_name": "CN=Let's Encrypt Authority X3, O=Let's Encrypt, C=US",
            "name_value": "example.com",
            "min_cert_id": 541884289,
            "last_observed": 1699123200,
            "cert_link": "/541884289.pem",
        }
    ]
    mock_resp = MagicMock()
    mock_resp.json.return_value = sample_data
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    result = client.search("example.com")
    assert len(result) == 1
    assert result[0]["ID"] == 541884289
    mock_get.assert_called_once_with(ANY, timeout=1)

@patch("requests.Session.get")
def test_search_retry(mock_get, client):
    mock_resp_fail = MagicMock()
    mock_resp_fail.raise_for_status.side_effect = requests.RequestException("Fail")
    mock_get.return_value = mock_resp_fail

    with pytest.raises(RuntimeError):
        client.search("test.com")
    assert mock_get.call_count == 1  # retries=1

@patch("requests.Session.get")
def test_fetch_pem(mock_get, client):
    mock_resp = MagicMock()
    mock_resp.text = "-----BEGIN CERTIFICATE-----...-----END CERTIFICATE-----"
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    pem = client.fetch_pem(123)
    assert "CERTIFICATE" in pem
    mock_get.assert_called_once()