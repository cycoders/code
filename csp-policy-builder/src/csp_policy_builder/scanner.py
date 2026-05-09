import base64
import hashlib
import logging
from typing import List, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, SoupStrainer

from .types import Resource, ScanConfig


logger = logging.getLogger(__name__)


class Scanner:
    """Scans websites for CSP-relevant resources."""

    def __init__(self, config: ScanConfig):
        self.config = config
        self.session = requests.Session()
        self.session.headers["User-Agent"] = self.config.user_agent
        self.visited: Set[str] = set()
        self.resources: List[Resource] = []

    def scan(self) -> List[Resource]:
        """Perform full scan."""
        for url in self.config.urls:
            self._scan_url(url, depth=0)
        return self.resources

    def _scan_url(self, url: str, depth: int) -> None:
        if depth > self.config.max_depth:
            return
        if len(self.visited) >= self.config.max_pages:
            return
        if any(pat in url for pat in self.config.ignore_patterns):
            return
        if url in self.visited:
            return

        self.visited.add(url)
        logger.debug(f"Scanning {url} (depth={depth})")

        try:
            resp = self.session.get(url, timeout=15, allow_redirects=True)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            base_url = resp.url
            self._extract_resources(soup, base_url)

            # Recursive links (limited)
            for tag in soup.find_all(["a", "link"], limit=10):
                href = tag.get("href")
                if href and not tag.get("rel") == "nofollow":  # heuristic
                    next_url = urljoin(base_url, href)
                    parsed_next = urlparse(next_url)
                    if parsed_next.scheme in ("http", "https"):
                        self._scan_url(next_url, depth + 1)
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")

    def _extract_resources(self, soup: BeautifulSoup, base_url: str) -> None:
        """Extract resources from soup."""

        # Inline scripts/styles
        for script in soup.find_all("script"):
            self._handle_inline(script.string, "script-src", base_url)
        for style in soup.find_all("style"):
            self._handle_inline(style.string, "style-src", base_url)

        # External resources
        resource_tags = {
            "script": "script-src",
            "link": "style-src",
            "img": "img-src",
            "iframe": "frame-src",
            "source": "media-src",
            "audio,video": "media-src",
            "object": "object-src",
        }
        for tag_name, directive in resource_tags.items():
            for tag in soup.select(tag_name):
                src = tag.get("src") or tag.get("data")
                if src:
                    full_url = urljoin(base_url, src)
                    parsed = urlparse(full_url)
                    res = Resource(
                        url=full_url,
                        scheme=parsed.scheme,
                        host=parsed.netloc or None,
                        path=parsed.path,
                        directive=directive,
                        is_inline=False,
                    )
                    self.resources.append(res)

    def _handle_inline(self, content: str | None, directive: str, base_url: str) -> None:
        if not content or not content.strip():
            return
        content_bytes = content.strip().encode("utf-8")
        sha256_hash = hashlib.sha256(content_bytes).digest()
        b64_hash = base64.b64encode(sha256_hash).decode("ascii")
        hash_val = f"'sha256-{b64_hash}'"
        res = Resource(
            url=f"inline:{directive}",
            scheme="inline",
            host=None,
            path="",
            directive=directive,
            is_inline=True,
            hash_value=hash_val,
        )
        self.resources.append(res)
