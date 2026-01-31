from typing import Dict, Tuple
import statistics
from .types import HeaderStatus, HeaderCheck
from .utils import parse_csp

SECURITY_HEADERS = {
    'strict-transport-security': {},
    'content-security-policy': {},
    'content-security-policy-report-only': {},
    'permissions-policy': {},
    'referrer-policy': {},
    'x-frame-options': {},
    'x-content-type-options': {},
    'x-xss-protection': {},
    'cross-origin-resource-policy': {},
    'cross-origin-opener-policy': {},
    'cross-origin-embedder-policy': {},
    'clear-site-data': {},
}

VALID_REFERRER_POLICIES = {
    'no-referrer', 'no-referrer-when-downgrade', 'origin',
    'origin-when-cross-origin', 'same-origin', 'strict-origin',
    'strict-origin-when-cross-origin', 'unsafe-url'
}


def check_security_headers(headers: Dict[str, str]) -> Dict[str, HeaderCheck]:
    """Check all security headers."""
    checks = {}
    header_names = list(SECURITY_HEADERS.keys())
    for name in header_names:
        value = headers.get(name.lower())
        check = _check_header(name, value)
        checks[name] = check
    return checks


def _check_header(name: str, value: str) -> HeaderCheck:
    if not value:
        return HeaderCheck(
            status=HeaderStatus.MISSING,
            score=0,
            reason="Header not present",
            recommendation=f"Add {name}",
        )
    if name == 'strict-transport-security':
        return _check_hsts(value)
    elif name == 'content-security-policy':
        return _check_csp(value)
    elif name == 'x-content-type-options':
        status = HeaderStatus.PRESENT if value.lower() == 'nosniff' else HeaderStatus.INVALID
        score = 10 if status == HeaderStatus.PRESENT else 2
        return HeaderCheck(status=status, score=score, reason=str(value), recommendation="")
    elif name == 'referrer-policy':
        if value.lower() in VALID_REFERRER_POLICIES:
            return HeaderCheck(status=HeaderStatus.PRESENT, score=10, reason="Good policy", recommendation="")
        else:
            return HeaderCheck(status=HeaderStatus.INVALID, score=3, reason=f"Invalid: {value}", recommendation="Use strict-origin-when-cross-origin")
    elif name == 'permissions-policy':
        return HeaderCheck(status=HeaderStatus.PRESENT, score=8, reason="Present", recommendation="Tighten features")
    else:
        return HeaderCheck(status=HeaderStatus.PRESENT, score=7, reason="Present", recommendation="Review config")


def _check_hsts(value: str) -> HeaderCheck:
    parts = [p.strip() for p in value.split(';')]
    max_age = 0
    subdomains = False
    preload = False
    for part in parts:
        if part.startswith('max-age='):
            max_age = int(part[8:])
        elif part == 'includesubdomains':
            subdomains = True
        elif part == 'preload':
            preload = True
    score = 0
    reason = []
    if max_age >= 31536000:
        score += 6
    else:
        reason.append(f"max-age={max_age} too low (min 1y)")
    if subdomains:
        score += 2
    if preload:
        score += 2
    rec = "Add includeSubDomains; preload if eligible"
    return HeaderCheck(status=HeaderStatus.PRESENT, score=min(score, 10), reason='; '.join(reason) or 'Good', recommendation=rec)


def _check_csp(value: str) -> HeaderCheck:
    try:
        directives = parse_csp(value)
        script_src = directives.get('script-src', [])
        score = 8
        reason = []
        if "'unsafe-inline'" in script_src:
            score -= 4
            reason.append("unsafe-inline in script-src")
        if "'unsafe-eval'" in script_src:
            score -= 3
            reason.append("unsafe-eval")
        if not any(h.startswith('sha') for h in script_src) and 'nonce' not in ' '.join(script_src).lower():
            reason.append("No hashes/nonces")
        rec = "Use hashes/nonces instead of unsafe-inline"
        return HeaderCheck(status=HeaderStatus.PRESENT, score=max(0, score), reason='; '.join(reason) or 'Good', recommendation=rec)
    except Exception:
        return HeaderCheck(status=HeaderStatus.INVALID, score=1, reason="Parse error", recommendation="Fix syntax")
