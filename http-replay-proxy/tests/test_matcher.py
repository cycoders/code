import pytest
from http_replay_proxy.matcher import requests_match

@pytest.fixture
def sample_req():
    return {
        'method': 'GET',
        'path': '/api/users/1',
        'query': {'limit': '10'},
        'headers': {'authorization': 'Bearer tok', 'user-agent': 'curl/7.0'}
    }

def test_requests_match_identical(sample_req):
    assert requests_match(sample_req, sample_req)

def test_requests_match_method_diff(sample_req):
    other = sample_req.copy()
    other['method'] = 'POST'
    assert not requests_match(sample_req, other)

def test_requests_match_path_diff(sample_req):
    other = sample_req.copy()
    other['path'] = '/api/posts/1'
    assert not requests_match(sample_req, other)

def test_requests_match_query_diff(sample_req):
    other = sample_req.copy()
    other['query'] = {'page': '1'}
    assert not requests_match(sample_req, other)

def test_requests_match_header_diff(sample_req):
    other = sample_req.copy()
    other['headers'] = sample_req['headers'].copy()
    other['headers']['authorization'] = 'Bearer bad'
    assert not requests_match(sample_req, other)

def test_requests_match_ignore_other_header(sample_req):
    other = sample_req.copy()
    other['headers']['x-foo'] = 'bar'
    del sample_req['headers']['x-foo']  # noqa
    assert requests_match(sample_req, other)