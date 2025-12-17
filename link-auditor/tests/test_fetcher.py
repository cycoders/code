import pytest

from pytest_httpx import HTTPXMock

import asyncio
from link_auditor.fetcher import fetch_url, create_link_result
from link_auditor.settings import Settings


@pytest.mark.asyncio
async def test_fetch_success(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://test.ok",
        status_code=200,
        headers={},
        content=b"ok",
    )
    client = httpx.AsyncClient()
    settings = Settings(timeout=5.0)
    result = await fetch_url(client, "https://test.ok", settings)
    assert result["status_code"] == 200
    assert result["error"] is None


@pytest.mark.asyncio
async def test_fetch_error(httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="https://test.fail", status_code=404)
    client = httpx.AsyncClient()
    result = await fetch_url(client, "https://test.fail", Settings())
    assert result["status_code"] == 404


@pytest.mark.asyncio
async def test_fetch_timeout(httpx_mock: HTTPXMock):
    httpx_mock.add_response(url="https://test.timeout", status_code=408)
    client = httpx.AsyncClient()
    result = await fetch_url(client, "https://test.timeout", Settings(timeout=0.1))
    assert "Timeout" in result["error"]
