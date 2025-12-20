import asyncio
import time
import random
from typing import Optional

import aiohttp
from aiohttp import web
from urllib.parse import urljoin

from .serialize import serialize_request, serialize_upstream_response, make_proxy_response, HOP_HEADERS

from .matcher import find_match

from .cassette import load_cassette, append_to_cassette

METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']

async def record_handler(req: web.Request, upstream: str, cassette_path: str) -> web.Response:
    """Handler for record mode: forward, capture, append to cassette."""
    start_time = time.perf_counter()
    upstream_url = urljoin(upstream, req.path_qs)

    # Forward request
    upstream_headers = {k: v for k, v in req.headers.items() if k.lower() not in HOP_HEADERS}
    body_bytes = await req.read()

    req_ser = await serialize_request(req)  # re-read? No, serialize before read, but await issue. Wait, serialize reads too.
    # Fix: serialize after read? But serialize needs read. Move read up.

    # Better: read body first
    body_bytes = await req.read()
    req_ser = {
        'method': req.method,
        'path': req.path,
        'query': dict(req.query),
        'headers': {k.lower(): v for k, v in req.headers.items() if k.lower() not in HOP_HEADERS},
        'body_b64': base64.b64encode(body_bytes).decode('ascii') if body_bytes else None,
        'content_type': req.content_type,
    }

    timeout = aiohttp.ClientTimeout(total=30)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        async with session.request(
            method=req.method,
            url=upstream_url,
            headers=upstream_headers,
            data=body_bytes,
        ) as up_resp:
            resp_ser = await serialize_upstream_response(up_resp)
            latency = time.perf_counter() - start_time

            interaction = {
                'request': req_ser,
                'response': resp_ser,
                'latency': round(latency, 3),
            }
            append_to_cassette(cassette_path, interaction)

            # Build response
            headers = dict(up_resp.headers)
            for h in HOP_HEADERS:
                headers.pop(h, None)
            resp = web.Response(
                status=up_resp.status,
                headers=headers,
                body=await up_resp.read()
            )
            return resp

async def replay_handler(req: web.Request, cassette_path: str, jitter: float, error_rate: float) -> web.Response:
    """Handler for replay mode."""
    interactions = load_cassette(cassette_path)
    body_bytes = await req.read()
    req_ser = {
        'method': req.method,
        'path': req.path,
        'query': dict(req.query),
        'headers': {k.lower(): v for k, v in req.headers.items() if k.lower() not in HOP_HEADERS},
        'body_b64': base64.b64encode(body_bytes).decode('ascii') if body_bytes else None,
        'content_type': req.content_type,
    }
    match = find_match(interactions, req_ser)
    if random.random() < error_rate:
        raise web.HTTPInternalServerError(text="Simulated error")
    if not match:
        raise web.HTTPNotFound(text="No matching cassette entry")
    latency = match['latency']
    if jitter > 0:
        latency *= random.uniform(max(0, 1 - jitter), 1 + jitter)
    await asyncio.sleep(latency)
    return await make_proxy_response(match['response'])

async def create_record_app(upstream: str, cassette_path: str) -> web.Application:
    """Create aiohttp app for record mode."""
    app = web.Application(client_max_size=10*1024*1024)
    async def handler(req):
        try:
            return await record_handler(req, upstream, cassette_path)
        except Exception as e:
            return web.Response(status=500, text=str(e))
    for method in METHODS:
        app.router.add_route(method, '/{tail:.*}', handler)
    return app

async def create_replay_app(cassette_path: str, jitter: float, error_rate: float) -> web.Application:
    """Create aiohttp app for replay mode."""
    app = web.Application(client_max_size=10*1024*1024)
    async def handler(req):
        try:
            return await replay_handler(req, cassette_path, jitter, error_rate)
        except web.HTTPException:
            raise
        except Exception as e:
            return web.Response(status=500, text=str(e))
    for method in METHODS:
        app.router.add_route(method, '/{tail:.*}', handler)
    return app

async def run_proxy(host: str, port: int, app_factory):
    """Run proxy server."""
    app = await app_factory()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f"Proxy running on http://{host}:{port} (Ctrl+C to stop)")
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        pass
    finally:
        await runner.cleanup()
