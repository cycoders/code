import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from websocket_tester.websocket_client import WSClient


@pytest.mark.asyncio
async def test_connect_success():
    with patch("websockets.connect", new_callable=AsyncMock) as mock_connect:
        mock_ws = AsyncMock()
        mock_connect.return_value = mock_ws
        client = WSClient("ws://test")
        await client.connect()
        mock_connect.assert_awaited_once()
        assert client.connected


@pytest.mark.asyncio
async def test_send_not_connected():
    client = WSClient("ws://test")
    with pytest.raises(RuntimeError, match="Not connected"):
        await client.send("msg")


@pytest.mark.asyncio
@patch("asyncio.wait_for")
async def test_recv_timeout(mock_waitfor):
    mock_waitfor.side_effect = asyncio.TimeoutError
    client = WSClient("ws://test")
    client._ws = AsyncMock()
    msg = await client.recv()
    assert msg is None


@pytest.mark.asyncio
async def test_close():
    client = WSClient("ws://test")
    client._ws = AsyncMock()
    client._ws.close = AsyncMock()
    await client.close()
    client._ws.close.assert_awaited_once()
    assert not client.connected