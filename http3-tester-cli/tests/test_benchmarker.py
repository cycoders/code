import pytest
from http3_tester_cli.benchmarker import run_benchmark


@pytest.mark.asyncio
async def test_run_benchmark(mocker):
    mocker.patch("http3_tester_cli.benchmarker.fetch_http3", return_value="mock_result")
    mocker.patch("http3_tester_cli.benchmarker.fetch_http2", return_value="mock_result")

    results = await run_benchmark("https://test", 1, True, "GET", 1000, [], False)

    assert "http3" in results
    assert "http2" in results
    assert len(results["http3"]["raw"]) == 1
