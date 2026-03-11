import pytest

from har_to_loadtest.model import HttpRequest
from har_to_loadtest.generators import get_generator_class
from har_to_loadtest.generators.base import Generator


@pytest.fixture
def sample_requests():
    return [
        HttpRequest(
            method="GET",
            url="https://api.example.com/users",
            headers={"authorization": "Bearer tok"},
            body=None,
            json_body=None,
        ),
        HttpRequest(
            method="POST",
            url="https://api.example.com/users",
            headers={"content-type": "application/json"},
            body='{"name":"test"}',
            json_body={"name": "test"},
        ),
    ]


@pytest.mark.parametrize("fmt", ["k6", "locust", "artillery"])
def test_generator_factory(fmt, sample_requests):
    cls = get_generator_class(fmt)
    gen: Generator = cls(sample_requests)
    assert isinstance(gen, Generator)
    assert len(gen.requests) == 2


def test_k6_generate(sample_requests):
    gen = get_generator_class("k6")(sample_requests)
    code = gen.generate()
    assert "http.get" in code
    assert "http.post" in code
    assert '"Authorization": "Bearer tok"' in code
    assert 'JSON.stringify({"name":"test"})' in code
    assert "vus: 10" in code


def test_locust_generate(sample_requests):
    gen = get_generator_class("locust")(sample_requests)
    code = gen.generate()
    assert "class HarUser" in code
    assert "@task" in code
    assert "json={"name": "test"}" in code


def test_artillery_generate(sample_requests):
    gen = get_generator_class("artillery")(sample_requests)
    code = gen.generate()
    assert "target: "https://api.example.com"" in code
    assert "method: POST" in code
    assert "json:\n            {"name": "test"}" in code
