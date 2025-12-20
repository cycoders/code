import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from pulse_cli.checker import check_single
from pulse_cli.models import EndpointConfig


@pytest.mark.asyncio
async def test_check_success():
    config = EndpointConfig(name="test", url="https://example.com")
    with patch("httpx.AsyncClient") as mock_client:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.text = "ok"
        mock_resp.content = b"ok"
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_resp
        result = await check_single(config)
        assert result.success
        assert result.status_code == 200
        assert result.response_time_ms is not None


@pytest.mark.asyncio
async def test_check_failure_status():
    config = EndpointConfig(name="test", url="https://example.com")
    with patch("httpx.AsyncClient") as mock_client:
        mock_resp = AsyncMock()
        mock_resp.status_code = 500
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_resp
        result = await check_single(config)
        assert not result.success