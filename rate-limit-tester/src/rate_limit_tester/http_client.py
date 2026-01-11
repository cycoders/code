import asyncio
from typing import Dict, Optional

import httpx
from httpx import Limits, Timeout

from ..config import Config
from .models import Headers


class RateLimitClient:
    """httpx client with auth/config."""

    def __init__(self, config: Config):
        limits = Limits(max_keepalive_connections=5, max_connections=100)
        timeout = Timeout(config.timeout)
        self.client = httpx.AsyncClient(limits=limits, timeout=timeout)
        self.config = config

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.client.aclose()

    async def head(self, url: str, **kwargs) -> httpx.Response:
        """HEAD with retries/backoff."""
        return await self._request("HEAD", url, **kwargs)

    async def get(self, url: str, **kwargs) -> httpx.Response:
        """GET with retries."""
        return await self._request("GET", url, **kwargs)

    async def _request(self, method: str, url: str, retries: int = 0, **kwargs) -> httpx.Response:
        kwargs.setdefault("headers", self.config.headers)
        try:
            resp = await self.client.request(method, url, **kwargs)
            if resp.status_code == 429 and retries < self.config.max_retries:
                await asyncio.sleep(self.config.backoff_factor ** retries)
                return await self._request(method, url, retries + 1, **kwargs)
            return resp
        except httpx.RequestError as e:
            raise RuntimeError(f"HTTP error: {e}") from e
