from typing import Dict, List
from urllib.parse import urlparse, urljoin


def parse_csp(value: str) -> Dict[str, List[str]]:
    """Parse CSP header into directives and values."""
    directives = {}
    for part in value.split(';'):
        part = part.strip()
        if ':' in part:
            name, rest = part.split(':', 1)
            name = name.strip().lower()
            values = [v.strip().strip("'\"") for v in rest.split() if v.strip()]
            directives[name] = values
    return directives


def extract_domains(srcs: set[str], base_url: str) -> set[str]:
    """Extract wildcard domains from src attributes."""
    domains = set()
    for src in srcs:
        full_url = urljoin(base_url, src)
        parsed = urlparse(full_url)
        if parsed.netloc:
            domains.add(f"{parsed.scheme}://{parsed.netloc}*")
    return domains


def compute_sha384(content: str) -> str:
    """Compute SHA-384 hash for CSP."""
    from hashlib import sha384
    return sha384(content.encode('utf-8')).hexdigest()
