from typing import Set
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from .utils import extract_domains


class CSPGenerator:
    """Generates strict CSP from HTML content."""

    def generate(self, html: str, base_url: str) -> str:
        """Analyze HTML, compute hashes, build policy."""
        soup = BeautifulSoup(html, 'html.parser')
        script_srcs: Set[str] = set()
        script_hashes: Set[str] = set()
        style_srcs: Set[str] = set()
        style_hashes: Set[str] = set()

        for tag in soup.find_all(['script', 'style']):
            if tag.name == 'script':
                srcs, hashes = script_srcs, script_hashes
            else:
                srcs, hashes = style_srcs, style_hashes

            src = tag.get('src') or tag.get('href')
            if src:
                srcs.add(src)
            else:
                content = (tag.string or '').strip()
                if content:
                    h = hashlib.sha384(content.encode('utf-8')).hexdigest()
                    hashes.add(f"'sha384-{h}'")

        all_domains = extract_domains(script_srcs | style_srcs, base_url)
        domains_str = ' '.join(sorted(all_domains)) if all_domains else ''

        directives = [
            "default-src 'self'",
            f"script-src 'self' {domains_str} {' '.join(sorted(script_hashes))}",
            f"style-src 'self' {domains_str} {' '.join(sorted(style_hashes))} 'unsafe-inline'",
            "img-src 'self' data: https: blob:",
            "font-src 'self' data: https:",
            "connect-src 'self' https: wss:",
            "media-src 'self' https: blob:",
            "frame-src 'self' https:",
            "child-src 'self' https:",
            "frame-ancestors 'none'",
            "form-action 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "block-all-mixed-content",
            "upgrade-insecure-requests",
        ]
        policy = '; '.join(directives) + ';'
        return policy
