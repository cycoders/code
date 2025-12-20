import base64
import time
from typing import Dict, Any, Optional
from aiohttp import web, ClientResponse

HOP_HEADERS = {
    'host', 'content-length', 'transfer-encoding', 'connection',
    'keep-alive', 'proxy-authenticate', 'proxy-authorization',
    'te', 'trailers', 'upgrade'
}

MATCH_HEADERS = {
    'authorization', 'x-api-key', 'x-user-id', 'user-agent', 'accept'
}

def serialize_request(req: web.Request) -> Dict[str, Any]:
    """Serialize request to dict for storage/matching."""
    body_bytes = await req.read()
    body_b64 = base64.b64encode(body_bytes).decode('ascii') if body_bytes else None
    return {
        'method': req.method,
        'path': req.path,
        'query': dict(req.query),
        'headers': {k.lower(): v for k, v in req.headers.items() if k.lower() not in HOP_HEADERS},
        'body_b64': body_b64,
        'content_type': req.content_type,
    }

async def serialize_upstream_response(up_resp: ClientResponse) -> Dict[str, Any]:
    """Serialize upstream response."""
    body_bytes = await up_resp.read()
    ct = up_resp.headers.get('content-type', '').split(';')[0].strip()
    body_b64 = base64.b64encode(body_bytes).decode('ascii') if body_bytes else None
    headers = {k.lower(): v for k, v in up_resp.headers.items() if k.lower() not in HOP_HEADERS}
    return {
        'status': up_resp.status,
        'headers': headers,
        'body_b64': body_b64,
        'content_type': ct,
    }

async def make_proxy_response(inter: Dict[str, Any]) -> web.Response:
    """Make response from cassette interaction."""
    resp_data = inter['response']
    body_bytes = base64.b64decode(resp_data['body_b64']) if resp_data['body_b64'] else b''
    headers = dict(resp_data['headers'])
    headers['content-length'] = str(len(body_bytes))
    if resp_data['content_type']:
        headers['content-type'] = resp_data['content_type']
    return web.Response(
        status=resp_data['status'],
        headers=headers,
        body=body_bytes
    )