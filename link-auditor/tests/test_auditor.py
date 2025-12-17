import pytest
from pytest_httpx import HTTPXMock

import asyncio
from link_auditor.auditor import audit_links
from link_auditor.settings import Settings


@pytest.mark.asyncio
async def test_audit_links(httpx_mock: HTTPXMock):
    httpx_mock.add_response("https://test1", json={})
    httpx_mock.add_response("https://test2", status_code=404)
    settings = Settings(concurrency=2, timeout=1.0)
    results = await audit_links(["https://test1", "https://test2"], settings)
    statuses = [r["status_code"] for r in results]
    assert 200 in statuses
    assert 404 in statuses
