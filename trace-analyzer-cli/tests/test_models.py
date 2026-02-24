import pytest
from trace_analyzer_cli.models import Span


@pytest.fixture
def sample_span():
    return {
        "traceID": "1",
        "spanID": "a",
        "operationName": "test",
        "startTime": 1000000,
        "duration": 500000,
        "tags": {"service.name": "test", "error": "true"},
    }


def test_span_parsing(sample_span):
    span = Span.model_validate(sample_span)
    assert span.service == "test"
    assert span.is_error is True
    assert span.duration_sec == 0.5
    assert span.start_time_sec == 1.0


def test_missing_tags(sample_span):
    del sample_span["tags"]
    span = Span.model_validate(sample_span)
    assert span.service == "unknown"
    assert span.is_error is False
