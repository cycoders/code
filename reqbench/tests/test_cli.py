import pytest
from reqbench.tests.conftest import invoke


def test_bench_help(invoke):
    result = invoke(["bench", "--help"])
    assert result.exit_code == 0
    assert "Benchmark HTTP requests" in result.stdout


def test_version(invoke):
    result = invoke(["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_no_url(invoke):
    result = invoke(["bench"])
    assert result.exit_code == 2
    assert "URL required" in result.stdout


def test_valid_simple(invoke):
    result = invoke(["bench", "https://httpbin.org/get"])
    assert result.exit_code == 0  # Would run if no mocks