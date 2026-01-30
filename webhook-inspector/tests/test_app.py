import pytest
from httpx import AsyncClient

from webhook_inspector.app import create_app


@pytest.mark.asyncio
async def test_webhook_endpoint(app, client: AsyncClient):
    resp = await client.post("/test", json={"test": True}, headers={"X-Custom-Sig": "test"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["received"]


@pytest.mark.asyncio
async def test_dashboard(app, client: AsyncClient):
    resp = await client.get("/")
    assert resp.status_code == 200
    assert b"Webhook Inspector" in resp.content
