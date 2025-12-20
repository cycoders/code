import asyncio
import re
import socket
import ssl
import time
from datetime import datetime
from typing import List

import httpx

from .models import EndpointConfig, CheckResult


async def check_single(config: EndpointConfig) -> CheckResult:
    """Perform full health check on one endpoint. Handles all errors gracefully."""
    url_str = str(config.url)
    start = time.perf_counter()
    status_code = None
    resp_time = None
    content_len = None
    content_text = ""
    cert_days = None
    success = False

    # HTTP check
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0), follow_redirects=True
        ) as client:
            resp = await client.get(url_str)
            resp_time = (time.perf_counter() - start) * 1000
            status_code = resp.status_code
            content_text = resp.text
            content_len = len(resp.content)
    except Exception:
        pass  # Fail silently, attrs None

    # Assertions
    if status_code is not None:
        success = status_code in config.expected_status
    if resp_time is not None:
        success = success and resp_time <= config.max_resp_time
    if config.content_match and content_text:
        success = success and bool(re.search(config.content_match, content_text, re.IGNORECASE))

    # Cert check
    if config.check_cert:
        try:
            hostname = config.url.host
            port = config.url.port or 443
            context = ssl.create_default_context()
            with socket.create_connection((str(hostname), port), timeout=5.0) as sock:
                with context.wrap_socket(sock, server_hostname=str(hostname)) as ssock:
                    cert = ssock.getpeercert()
                    not_after = cert["notAfter"]
                    dt = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                    delta = dt - datetime.utcnow()
                    cert_days = max(0, delta.days)
        except Exception:
            cert_days = -1.0

    return CheckResult(
        timestamp=datetime.now(),
        endpoint_name=config.name,
        url=url_str,
        status_code=status_code,
        response_time_ms=resp_time,
        content_length=content_len,
        cert_expiry_days=cert_days,
        success=success,
    )


async def check_endpoints(configs: List[EndpointConfig], storage) -> List[CheckResult]:
    """Async batch check + auto-store."""
    tasks = [check_single(conf) for conf in configs]
    results = await asyncio.gather(*tasks)
    for result in results:
        storage.store(result)
    return results