import httpx
from typing import Dict, Optional

from .models import HttpResponse

from .cache_parser import parse_cache_policy


def fetch_url(url: str, extra_headers: Optional[Dict[str, str]] = None) -> HttpResponse:
    """Fetch single URL and parse cache policy."""
    headers = extra_headers or {}
    try:
        resp = httpx.get(url, headers=headers, follow_redirects=True, timeout=10.0)
        resp.raise_for_status()
        headers_lower = {k.lower(): v for k, v in resp.headers.items()}
        hr = HttpResponse(
            url=url,
            status_code=resp.status_code,
            headers=headers_lower,
            timestamp=None  # live, no precise ts
        )
        hr.cache_policy = parse_cache_policy(headers_lower)
        return hr
    except httpx.RequestError as e:
        raise RuntimeError(f"Failed to fetch {url}: {e}")
