import asyncio
import time
import urllib.parse
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

from aiohttp import ClientSession, ClientTimeout, TCPConnector
from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived, HttpHeader, HttpDataReceived
from aioquic.h0.connection import H0Connection, H0Datagram
from aioquic.h0.protocol import HttpRequest, HttpResponse


@dataclass
class FetchResult:
    protocol: str
    status: int
    connect_time: float  # ms
    ttfb: float         # ms
    total_time: float   # ms
    body_size: int      # bytes
    error: Optional[str] = None


async def fetch_http2(
    url: str, method: str, max_body: int, headers: List[str]
) -> FetchResult:
    """Fetch via HTTP/2 (or 1.1 fallback) with timings."""
    start = time.perf_counter()
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("Only HTTPS supported")

    connector = TCPConnector(limit=1, enable_cleanup_closed=True)
    timeout = ClientTimeout(total=30)
    hdict = {}
    for h in headers:
        k, v = h.split(":", 1)
        hdict[k.strip()] = v.strip()

    async with ClientSession(
        connector=connector, timeout=timeout, headers=hdict
    ) as session:
        connect_start = time.perf_counter()
        try:
            async with session.request(method, url) as resp:
                connect_time = (time.perf_counter() - connect_start) * 1000
                ttfb_start = time.perf_counter()
                body = await resp.read()
                body_size = min(len(body), max_body)
                ttfb = (time.perf_counter() - ttfb_start) * 1000
                total_time = (time.perf_counter() - start) * 1000
                return FetchResult(
                    "HTTP/2",
                    resp.status,
                    connect_time,
                    ttfb,
                    total_time,
                    body_size,
                )
        except Exception as e:
            total_time = (time.perf_counter() - start) * 1000
            return FetchResult("HTTP/2", 0, 0, 0, total_time, 0, str(e))


async def fetch_http3(
    url: str, method: str, max_body: int, headers: List[str], verbose: bool = False
) -> FetchResult:
    """Fetch via HTTP/3 (QUIC) with low-level timings. Adapted from aioquic examples."""
    start = time.perf_counter()
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    port = parsed.port or 443
    path = parsed.path or "/"
    if parsed.query:
        path += "?" + parsed.query

    config = QuicConfiguration(is_client=True)
    # Load system certs (platform auto)

    hdict = {b":method": method.encode(), b":path": path.encode(), b":authority": host.encode(), b"user-agent": b"http3-tester/0.1"}
    for h in headers:
        k, v = h.split(":", 1)
        hdict[k.strip().encode().lower()] = v.strip().encode()

    request = HttpRequest(**hdict)

    connect_start = time.perf_counter()
    try:
        async with connect(host, port, configuration=config) as client:
            connect_time = (time.perf_counter() - connect_start) * 1000
            if verbose:
                print(f"QUIC connected in {connect_time:.1f}ms")

            client.send_request_stream(request)

            ttfb_start = time.perf_counter()
            response: Optional[HttpResponse] = None
            body_bytes = 0
            async for event in client:
                if isinstance(event, StreamDataReceived) and event.stream_id == request.stream_id:
                    body_bytes += len(event.data)
                    if body_bytes > max_body:
                        break
                elif isinstance(event, HttpHeader) and event.content == b"response_received":
                    response = event.response
                    ttfb = (time.perf_counter() - ttfb_start) * 1000
                    break
                if body_bytes >= max_body:
                    break

            total_time = (time.perf_counter() - start) * 1000
            if response:
                return FetchResult(
                    "HTTP/3",
                    response.status_code,
                    connect_time,
                    ttfb,
                    total_time,
                    body_bytes,
                )
            else:
                raise ValueError("No response received")
    except Exception as e:
        total_time = (time.perf_counter() - start) * 1000
        return FetchResult("HTTP/3", 0, 0, 0, total_time, 0, str(e))
