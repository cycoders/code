import asyncio
import time
from typing import Optional

import httpx

from .settings import Settings


def create_link_result(
    url: str,
    resolved_url: Optional[str],
    status_code: Optional[int],
    response_time: Optional[float],
    content_length: Optional[int],
    error: Optional[str],
) -> dict:
    """Dataclass-like for result."""
    return {
        "url": url,
        "resolved_url": resolved_url,
        "status_code": status_code,
        "response_time": response_time,
        "content_length": content_length,
        "error": error,
    }


async def fetch_url(client: httpx.AsyncClient, url: str, settings: Settings) -> dict:
    """Fetch single URL with retries."""
    error = None
    for attempt in range(settings.max_retries + 1):
        try:
            start_time = time.perf_counter()
            resp = await client.get(url, follow_redirects=settings.follow_redirects)
            elapsed = time.perf_counter() - start_time
            return create_link_result(
                url,
                str(resp.url),
                resp.status_code,
                elapsed,
                len(resp.content),
                None,
            )
        except httpx.RequestError as e:
            error = f"{e.__class__.__name__}: {str(e)}"
            if attempt < settings.max_retries:
                await asyncio.sleep(2**attempt)
    return create_link_result(url, None, None, None, None, error)
