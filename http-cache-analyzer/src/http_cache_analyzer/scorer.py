from typing import Tuple, List

from .models import CachePolicy

_STATIC_EXTS = {'.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf'}


def get_resource_type(url: str) -> str:
    if any(url.lower().endswith(ext) for ext in _STATIC_EXTS):
        return 'static'
    return 'dynamic'


def score_policy(policy: CachePolicy, url: str) -> Tuple[int, str]:
    """Score policy 0-100, return suggestion."""
    if not policy:
        return 0, "No cache policy headers"

    score = 0
    suggestions: List[str] = []
    rtype = get_resource_type(url)
    directives = [d.name for d in policy.directives]

    has_no_cache = 'no-cache' in directives
    has_no_store = 'no-store' in directives
    has_immutable = 'immutable' in directives
    has_validation = bool(policy.etag or policy.last_modified)

    if rtype == 'static':
        if policy.max_age and policy.max_age >= 31536000:  # 1y
            score += 40
        elif policy.max_age and policy.max_age >= 3600:
            score += 20
        if has_immutable:
            score += 20
        if not has_no_store:
            score += 10
        if score < 60:
            suggestions.append("Long max-age (1y+), immutable for static")
    else:  # dynamic
        if has_no_cache or has_no_store:
            score += 40
        elif policy.max_age and policy.max_age <= 60:
            score += 25
        if has_validation:
            score += 20
        if score < 60:
            suggestions.append("no-cache/no-store or short max-age + ETag for dynamic")

    if has_validation:
        score += min(20, 20 - len(suggestions) * 5)

    score = min(100, max(0, score))
    sugg = '; '.join(suggestions)[:50] + '...' if suggestions else 'Good!'

    return score, sugg
