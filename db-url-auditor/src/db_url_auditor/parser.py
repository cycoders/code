from urllib.parse import urlparse, parse_qs

from .models import AuditResult

SCHEMES = {"postgresql", "postgres", "mysql", "mongodb", "redis", "mssql"}

class ParseError(Exception):
    pass

def parse_url(raw: str) -> AuditResult:
    if not raw or " " in raw:
        raise ParseError("URL contains whitespace or is empty")
    parsed = urlparse(raw)
    if parsed.scheme not in SCHEMES:
        raise ParseError(f"Unsupported scheme: {parsed.scheme}")
    return AuditResult(url=raw, scheme=parsed.scheme)