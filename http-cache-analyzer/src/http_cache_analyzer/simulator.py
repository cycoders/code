from typing import Dict, Any
from collections import defaultdict
import random

from .models import HttpResponse


def simulate_sequence(responses: list[HttpResponse]) -> Dict[str, Any]:
    """Replay HAR sequence using timestamps for realistic staleness."""
    if not responses:
        return {'hit_rate': 0, 'hits': 0, 'total': 0}

    # Sort by timestamp
    responses = sorted(responses, key=lambda r: r.timestamp or datetime.min)
    base_time = responses[0].timestamp

    cache: Dict[str, tuple[float, 'CachePolicy']] = {}  # url: (serve_time, policy)
    hits, total = 0, len(responses)

    for resp in responses:
        url = str(resp.url)
        req_time = (resp.timestamp - base_time).total_seconds() if resp.timestamp and base_time else 0

        cached = cache.get(url)
        if cached:
            cache_time, policy = cached
            age = req_time - cache_time
            if policy.max_age and age < policy.max_age:
                hits += 1
                continue  # fresh hit
            if policy.etag or policy.last_modified:
                hits += 1  # revalidate -> hit

        # miss/update cache
        cache[url] = (req_time, resp.cache_policy)

    hit_rate = (hits / total) * 100 if total else 0
    return {'mode': 'sequence', 'hit_rate': hit_rate, 'hits': hits, 'total': total}


def simulate_burst(responses: list[HttpResponse], num_requests: int = 1000) -> Dict[str, Any]:
    """Simulate burst traffic across unique responses."""
    if not responses:
        return {'hit_rate': 0, 'hits': 0, 'total': 0}

    cache: set[str] = set()
    hits, total = 0, num_requests

    for _ in range(num_requests):
        resp = random.choice(responses)
        url = str(resp.url)
        if url in cache:
            # simplistic: hit unless strict no-cache
            if any(d.name in ('no-store', 'private') for d in resp.cache_policy.directives):
                pass
            else:
                hits += 1
        else:
            cache.add(url)

    hit_rate = (hits / total) * 100
    return {'mode': 'burst', 'hit_rate': hit_rate, 'hits': hits, 'total': total}
