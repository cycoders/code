import asyncio
import httpx
from typing import List, Dict

from .fetcher import fetch_url
from .settings import Settings


async def audit_links(links: List[str], settings: Settings) -> List[Dict]:
    """Audit all links concurrently."""
    limits = httpx.Limits(
        max_keepalive_connections=20,
        max_connections=settings.concurrency,
    )
    headers = {"User-Agent": "link-auditor/0.1.0 (+https://github.com/cycoders/code)"}

    async with httpx.AsyncClient(
        limits=limits,
        timeout=httpx.Timeout(settings.timeout),
        headers=headers,
    ) as client:
        semaphore = asyncio.Semaphore(settings.concurrency)

        async def bounded_fetch(url: str) -> Dict:
            async with semaphore:
                return await fetch_url(client, url, settings)

        tasks = [bounded_fetch(link) for link in links]
        results = await asyncio.gather(*tasks, return_exceptions=False)
    return results
