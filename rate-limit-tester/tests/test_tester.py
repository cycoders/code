import pytest

from rate_limit_tester.tester import RateLimitTester


@pytest.mark.asyncio
async def test_discover_parses_headers(mock_http):
    mock_http.get("/")("https://test.com", headers={"x-ratelimit-limit": "100", "retry-after": "60"})

    config = {"url": "https://test.com"}  # Simplified
    tester = RateLimitTester(config)
    info = await tester.discover()

    assert info.limit == 100
    assert info.retry_after == 60
    assert "x-ratelimit-limit" in info.headers_seen


@pytest.mark.asyncio
async def test_burst_binary_search(mock_http):
    # Mock high success low fail
    def mock_burst(url, n):
        return (n if n <= 50 else 40), (0 if n <= 50 else n - 40)

    tester = RateLimitTester({})
    tester._run_concurrent = mock_burst  # Patch for test
    burst = await tester.measure_burst(100)
    assert burst == 50
