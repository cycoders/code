from typing import List
import lxml.etree as etree
from urllib.parse import urljoin, urlparse
import aiohttp


def get_locs_from_xml(content_bytes: bytes) -> List[str]:
    """Extract <loc> URLs from sitemap XML (urlset or index)."""
    try:
        root = etree.fromstring(content_bytes)
        ns = {"sitemap": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = root.xpath(".//sitemap:loc/text() | .//loc/text()", namespaces=ns)
        return [loc.strip() for loc in locs if loc.strip()]
    except etree.XMLSyntaxError:
        return []


async def get_sitemap_urls(
    session: aiohttp.ClientSession,
    sitemap_url: str,
    base_url: str,
    max_depth: int = 3,
    current_depth: int = 0,
) -> List[str]:
    """Recursively fetch and extract page URLs from sitemap(s). Dedupes."""
    if current_depth > max_depth:
        return []

    try:
        async with session.get(sitemap_url, timeout=aiohttp.ClientTimeout(total=30)) as resp:
            if resp.status != 200:
                return []
            content = await resp.text(encoding="utf-8")
            content_bytes = content.encode("utf-8")
    except Exception as e:
        print(f"[yellow]Failed fetching sitemap {sitemap_url}: {e}[/yellow]")
        return []

    locs = get_locs_from_xml(content_bytes)
    urls: List[str] = []
    for loc in locs:
        full_url = urljoin(sitemap_url, loc)
        parsed = urlparse(full_url)
        if parsed.scheme not in ("http", "https"):
            continue
        if parsed.path.lower().endswith(".xml"):
            # Recurse on sub-sitemaps
            sub_urls = await get_sitemap_urls(session, full_url, base_url, max_depth, current_depth + 1)
            urls.extend(sub_urls)
        else:
            # Page URL
            urls.append(full_url)

    return list(set(urls))  # Deduplicate