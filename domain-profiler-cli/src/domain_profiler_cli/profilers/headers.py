import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Tuple


def get_headers_and_html(domain: str, port: int = 443, use_http: bool = False, timeout: float = 10.0) -> Tuple[Dict[str, str], Optional[str]]:
    """Fetch headers and HTML (for tech detection)."""
    protocol = "http" if use_http else "https"
    url = f"{protocol}://{domain}:{port}" if port != (80 if use_http else 443) else f"{protocol}://{domain}"

    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=0.1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers["User-Agent"] = "DomainProfiler/0.1.0"

    try:
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        headers = dict(resp.headers)
        html = resp.text if resp.status_code < 400 else None
        return headers, html
    except Exception:
        return {}, None