import time
import dns.resolver
import dns.exception
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from .models import PropagationResult, Status
from .resolvers import RESOLVERS


def query_single(
    resolver: Dict[str, str],
    domain: str,
    rdtype: str,
    expected: str,
    timeout: float,
) -> PropagationResult:
    ip = resolver["ip"]
    name = resolver["name"]
    location = resolver["location"]
    start = time.perf_counter()
    result = PropagationResult(name, ip, location, Status.ERROR, None, 0.0)

    try:
        dns_resolver = dns.resolver.Resolver(configure=False)
        dns_resolver.nameservers = [ip]
        dns_resolver.timeout = timeout
        dns_resolver.lifetime = timeout
        answers = dns_resolver.resolve(domain, rdtype)
        response = str(answers[0])
        latency = (time.perf_counter() - start) * 1000
        if response.rstrip(".") == expected.rstrip("."):
            result.status = Status.PROPAGATED
        else:
            result.status = Status.PENDING
        result.response = response
        result.latency = latency
    except dns.exception.Timeout:
        result.error = "Timeout"
        result.latency = (time.perf_counter() - start) * 1000
    except dns.resolver.NXDOMAIN:
        result.error = "NXDOMAIN"
        result.latency = (time.perf_counter() - start) * 1000
    except dns.resolver.NoAnswer:
        result.error = "NoAnswer"
        result.latency = (time.perf_counter() - start) * 1000
    except Exception as e:
        result.error = str(e)
        result.latency = (time.perf_counter() - start) * 1000

    return result


def check_propagation(
    domain: str,
    rdtype: str = "A",
    expected: str = None,
    resolvers: List[Dict[str, str]] = None,
    timeout: float = 5.0,
    max_workers: int = 20,
) -> List[PropagationResult]:
    if resolvers is None:
        resolvers = RESOLVERS
    if expected is None:
        raise ValueError("--expected is required for propagation checks")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(query_single, r, domain, rdtype, expected, timeout)
            for r in resolvers
        ]
        results = [future.result() for future in as_completed(futures)]

    # Sort: propagated first, then by latency
    results.sort(key=lambda r: (r.status != Status.PROPAGATED, r.latency))
    return results