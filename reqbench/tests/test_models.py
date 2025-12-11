import pytest
from pydantic import ValidationError
from reqbench.models import BenchmarkConfig


def test_valid_config():
    config = BenchmarkConfig(url="https://example.com")
    assert config.url == "https://example.com"
    assert config.method == "GET"
    assert config.clients == ["httpx", "requests"]


def test_invalid_client():
    with pytest.raises(ValidationError):
        BenchmarkConfig(url="https://example.com", clients=["invalid"])


def test_url_validation():
    with pytest.raises(ValidationError):
        BenchmarkConfig(url="not-a-url")


def test_bounds():
    config = BenchmarkConfig(url="https://example.com", concurrency=100, duration=60.0)
    assert config.concurrency == 100
    assert config.duration == 60.0