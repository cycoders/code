import pytest
import httpx
from unittest.mock import Mock, patch
from oauth_flow_tester.client import run_auth_code_flow, run_client_credentials


@patch("oauth_flow_tester.client.webbrowser")
@patch("oauth_flow_tester.client.httpx")
def test_auth_code_flow_success(mock_httpx, mock_browser, console_mock):
    mock_client = Mock()
    mock_httpx.Client.return_value.__enter__.return_value = mock_client
    mock_client.post.return_value.status_code = 200
    mock_client.post.return_value.json.return_value = {"access_token": "test_token"}

    result = run_auth_code_flow("http://test", "test", "http://cb", "read", True, console_mock)
    assert result["access_token"] == "test_token"


@patch("oauth_flow_tester.client.httpx")
def test_client_credentials_success(mock_httpx, console_mock):
    mock_client = Mock()
    mock_httpx.Client.return_value.__enter__.return_value = mock_client
    mock_client.post.return_value.status_code = 200
    mock_client.post.return_value.json.return_value = {"access_token": "test"}

    result = run_client_credentials("http://test", "id", "sec", console_mock)
    assert result is not None


@patch("oauth_flow_tester.client.httpx")
def test_client_credentials_fail(mock_httpx, console_mock):
    mock_client = Mock()
    mock_httpx.Client.return_value.__enter__.return_value = mock_client
    mock_client.post.return_value.status_code = 401

    result = run_client_credentials("http://test", "id", "bad", console_mock)
    assert result is None
