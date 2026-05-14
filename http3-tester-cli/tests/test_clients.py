import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock

from http3_tester_cli.clients import fetch_http2, fetch_http3, FetchResult


@pytest.mark.asyncio
async def test_fetch_http2_success(mocker):
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b"test body"

    mock_session = AsyncMock()
    mock_session.request.return_value.__aenter__.return_value = mock_resp

    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await fetch_http2("https://test.com", "GET", 1000, [])

    assert result.protocol == "HTTP/2"
    assert result.status == 200
    assert result.body_size == 8


@pytest.mark.asyncio
async def test_fetch_http2_error(mocker):
    mock_session = AsyncMock()
    mock_session.request.side_effect = Exception("Connection failed")

    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await fetch_http2("https://test.com", "GET", 1000, [])

    assert result.error == "Connection failed"
    assert result.status == 0


@pytest.mark.asyncio
async def test_fetch_http3(mocker):
    # Mock connect context
    mock_client = AsyncMock()
    mock_client.__aenter__ = lambda: mock_client
    mock_client.__aexit__ = lambda *a: None

    mock_event = MagicMock()
    mock_event.content = b"response_received"
    mock_event.response.status_code = 200
    mock_client.__aiter__.return_value.__anext__.return_value = mock_event

    with patch("aioquic.asyncio.connect", return_value=mock_client):
        result = await fetch_http3("https://test.com", "GET", 1000, [], verbose=False)

    assert result.protocol == "HTTP/3"
    assert result.status == 200
