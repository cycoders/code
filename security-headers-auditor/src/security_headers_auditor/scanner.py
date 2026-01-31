import requests
from typing import Dict, Any, Optional


class WebScanner:
    """Fetches web page with configurable session."""

    def __init__(self, timeout: int = 10, user_agent: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent or 'SecurityHeadersAuditor/0.1 (+https://github.com/cycoders/code)',
        })
        self.timeout = timeout

    def scan(self, url: str, fetch_html: bool = True) -> Dict[str, Any]:
        """Fetch URL, return headers/HTML."""
        try:
            resp = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            resp.raise_for_status()
            data: Dict[str, Any] = {
                'url': resp.url,
                'status_code': resp.status_code,
                'headers': dict(resp.headers),
            }
            if fetch_html:
                data['html'] = resp.text
            return data
        except requests.RequestException as e:
            raise ValueError(f"Failed to scan {url}: {str(e)}") from e
