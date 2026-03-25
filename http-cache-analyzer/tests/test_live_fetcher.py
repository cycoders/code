import pytest
import httpx
from unittest.mock import MagicMock

from http_cache_analyzer.live_fetcher import fetch_url


def test_fetch_url(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"cache-control": "max-age=100"}
    monkeypatch.setattr("httpx.get", lambda *args, **kwargs: mock_resp)

    resp = fetch_url("https://test.ex.com")
    assert resp.status_code == 200
    assert resp.cache_policy.max_age == 100
