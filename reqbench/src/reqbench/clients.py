import time
import httpx
import requests
import aiohttp
from typing import Dict, Any, Tuple, Callable, Awaitable

def create_sync_session(client_name: str) -> Tuple[Callable[[Dict[str, Any]], Dict[str, Any]], Any]:
    if client_name == "requests":
        session = requests.Session()
        def request(req: Dict[str, Any]) -> Dict[str, Any]:
            start = time.perf_counter()
            resp = session.request(
                method=req["method"],
                url=str(req["url"]),
                headers=req.get("headers"),
                params=req.get("params"),
                json=req.get("json"),
                data=req.get("data"),
                timeout=30.0,
            )
            latency = time.perf_counter() - start
            return {
                "status": resp.status_code,
                "latency": latency,
                "ok": resp.ok,
            }
        return request, session
    elif client_name == "httpx-sync":
        session = httpx.Client(timeout=30.0)
        def request(req: Dict[str, Any]) -> Dict[str, Any]:
            start = time.perf_counter()
            resp = session.request(
                method=req["method"],
                url=str(req["url"]),
                headers=req.get("headers"),
                params=req.get("params"),
                json=req.get("json"),
                data=req.get("data"),
            )
            latency = time.perf_counter() - start
            return {
                "status": resp.status_code,
                "latency": latency,
                "ok": resp.is_success,
            }
        return request, session
    else:
        raise ValueError(f"Unknown sync client: {client_name}")

async def create_async_session(client_name: str) -> Tuple[Awaitable[Dict[str, Any]], Any]:
    if client_name == "httpx":
        session = httpx.AsyncClient(timeout=30.0)
        async def request(req: Dict[str, Any]) -> Dict[str, Any]:
            start = time.perf_counter()
            resp = await session.request(
                method=req["method"],
                url=str(req["url"]),
                headers=req.get("headers"),
                params=req.get("params"),
                json=req.get("json"),
                data=req.get("data"),
            )
            latency = time.perf_counter() - start
            return {
                "status": resp.status_code,
                "latency": latency,
                "ok": resp.is_success,
            }
        return request, session
    elif client_name == "aiohttp":
        connector = aiohttp.TCPConnector(limit_per_host=200, ttl_dns_cache=300)
        session = aiohttp.ClientSession(connector=connector, timeout=aiohttp.ClientTimeout(total=30))
        async def request(req: Dict[str, Any]) -> Dict[str, Any]:
            kwargs: Dict[str, Any] = {
                "method": req["method"],
                "url": str(req["url"]),
            }
            for k in ["headers", "params", "json", "data"]:
                if k in req:
                    kwargs[k] = req[k]
            start = time.perf_counter()
            async with session.request(**kwargs) as resp:
                latency = time.perf_counter() - start
            return {
                "status": resp.status,
                "latency": latency,
                "ok": 200 <= resp.status < 400,
            }
        return request, session
    else:
        raise ValueError(f"Unknown async client: {client_name}")