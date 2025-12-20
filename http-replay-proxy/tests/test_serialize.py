import pytest
import base64
from unittest.mock import AsyncMock, MagicMock
from aiohttp import web
from http_replay_proxy.serialize import serialize_request, serialize_upstream_response

@pytest.mark.asyncio
async def test_serialize_request():
    req = MagicMock(spec=web.Request)
    req.method = 'POST'
    req.path = '/test'
    req.query = {'q': 'v'}
    req.headers = {'Auth': 'tok', 'Host': 'loc', 'Content-Length': '5'}
    req.content_type = 'app/json'
    req.read.return_value = b'{"foo":"bar"}'
    ser = await serialize_request(req)
    assert ser['method'] == 'POST'
    assert ser['path'] == '/test'
    assert ser['query'] == {'q': 'v'}
    assert ser['headers'] == {'auth': 'tok'}
    assert ser['content_type'] == 'app/json'
    assert ser['body_b64']

@pytest.mark.asyncio
async def test_serialize_upstream_response():
    up_resp = AsyncMock()
    up_resp.status = 200
    up_resp.headers = {'Content-Type': 'app/json', 'Host': 'ex'}
    up_resp.read.return_value = b'[]'
    ser = await serialize_upstream_response(up_resp)
    assert ser['status'] == 200
    assert 'content-type' in ser['headers']
    assert ser['body_b64'] == base64.b64encode(b'[]').decode()
