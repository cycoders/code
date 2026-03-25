import pytest
from datetime import datetime, timedelta

from http_cache_analyzer.models import HttpResponse, CachePolicy, CacheDirective, HttpUrl
from http_cache_analyzer.simulator import simulate_sequence, simulate_burst


@pytest.fixture
def sample_responses():
    responses = [
        HttpResponse(
            url=HttpUrl("https://ex.com/a"),
            status_code=200,
            headers={},
            timestamp=datetime.now(),
            cache_policy=CachePolicy(max_age=100),
        ),
        HttpResponse(
            url=HttpUrl("https://ex.com/a"),
            status_code=200,
            headers={},
            timestamp=datetime.now() + timedelta(seconds=50),
            cache_policy=CachePolicy(max_age=100),
        ),
    ]
    return responses


def test_simulate_sequence(sample_responses):
    sim = simulate_sequence(sample_responses)
    assert sim["hit_rate"] > 0
    assert sim["hits"] == 1  # second is fresh hit


def test_simulate_burst(sample_responses):
    sim = simulate_burst(sample_responses, 10)
    assert 0 < sim["hit_rate"] < 100
