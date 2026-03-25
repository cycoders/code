import re
from datetime import datetime

from .models import CachePolicy, CacheDirective


_EXPIRES_RE = re.compile(r'^(\w{3}),\s+(\d{2})\s+(\w{3})\s+(\d{4})\s+(\d{2}):(\d{2}):(\d{2})\s+GMT$')


def parse_cache_policy(headers: dict[str, str]) -> CachePolicy:
    """Parse Cache-Control, ETag, Expires, Last-Modified into structured policy."""
    cache_control = headers.get('cache-control', '').lower()
    directives = []

    for part in cache_control.split(','):
        part = part.strip()
        if not part:
            continue
        if '=' in part:
            name, value = part.split('=', 1)
            directives.append(CacheDirective(name=name.strip(), value=value.strip()))
        else:
            directives.append(CacheDirective(name=part))

    policy = CachePolicy(directives=directives)

    # Extract values
    for directive in directives:
        if directive.name == 'max-age' and directive.value:
            try:
                policy.max_age = int(directive.value)
            except ValueError:
                pass
        elif directive.name == 's-maxage' and directive.value:
            try:
                policy.s_maxage = int(directive.value)
            except ValueError:
                pass

    policy.etag = headers.get('etag')
    policy.last_modified = headers.get('last-modified')

    expires_str = headers.get('expires')
    if expires_str:
        match = _EXPIRES_RE.match(expires_str)
        if match:
            try:
                policy.expires = datetime.strptime(expires_str, '%a, %d %b %Y %H:%M:%S GMT')
            except ValueError:
                pass

    return policy
