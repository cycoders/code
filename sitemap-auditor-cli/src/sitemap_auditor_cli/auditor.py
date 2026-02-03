import asyncio
from time import perf_counter
from typing import List
from urllib.parse import urlparse
import aiohttp
from .types import AuditResult
from .parser import get_sitemap_urls
from .robots import get_disallow_paths


async def audit_sitemap(
    sitemap_url: str,
    concurrency: int = 50,
    timeout: float = 10.0,
    respect_robots: bool = True,
    max_sitemap_depth: int = 3,
    user_agent: str = "SitemapAuditorCLI/0.1.0 (+https://github.com/cycoders/code)",
) -> List[AuditResult]:
    """Perform full sitemap audit."""
    base_url = sitemap_url.rsplit("/", 1)[0] if "/" in sitemap_url else sitemap_url

    connector = aiohttp.TCPConnector(
        limit=concurrency * 2,
        limit_per_host=concurrency,
        ttl_dns_cache=300,
    )
    timeout_config = aiohttp.ClientTimeout(total=None)

    headers = {"User-Agent": user_agent}

    async with aiohttp.ClientSession(
        connector=connector, timeout=timeout_config, headers=headers
    ) as session:
        urls = await get_sitemap_urls(session, sitemap_url, base_url, max_sitemap_depth)
        if not urls:
            raise ValueError(f"No valid URLs extracted from {sitemap_url}")

        disallows = [] if not respect_robots else await get_disallow_paths(session, base_url)

        semaphore = asyncio.Semaphore(concurrency)
        tasks = [fetch_single_url(session, url, semaphore, timeout, disallows) for url in urls]
        raw_results = await asyncio.gather(*tasks)

        return [r for r in raw_results if isinstance(r, AuditResult)]


async def fetch_single_url(
    session: aiohttp.ClientSession,
    url: str,
    semaphore: asyncio.Semaphore,
    timeout: float,
    disallows: List[str],
) -> AuditResult:
    """Fetch and analyze single URL."""
    async with semaphore:
        # Quick robots check
        parsed = urlparse(url)
        if any(parsed.path.startswith(d) for d in disallows):
            return AuditResult(url=url, error="Blocked by robots.txt")

        start = perf_counter()
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=timeout), allow_redirects=True
            ) as resp:
                end = perf_counter()
                content = await resp.read()
                size = len(content)
                ct = resp.headers.get("content-type", "unknown").split(";")[0].strip()
                final_url = str(resp.url)
                return AuditResult(
                    url=url,
                    status_code=resp.status,
                    response_time=end - start,
                    size=size,
                    content_type=ct,
                    final_url=final_url,
                )
        except asyncio.TimeoutError:
            end = perf_counter()
            return AuditResult(url=url, error="Timeout", response_time=end - start)
        except aiohttp.ClientError as e:
            end = perf_counter()
            return AuditResult(url=url, error=str(e), response_time=end - start)
        except Exception as e:
            end = perf_counter()
            return AuditResult(url=url, error=str(e), response_time=end - start)