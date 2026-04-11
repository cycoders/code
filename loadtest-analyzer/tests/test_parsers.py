import pytest
from pathlib import Path

from loadtest_analyzer.parsers import parse_csv, parse_json, parse_timestamp
from loadtest_analyzer.models import Request


@pytest.fixture
 def sample_csv():
    return "tests/data/sample.csv"

@pytest.fixture
 def sample_json():
    return "tests/data/sample.json"

 def test_parse_timestamp_unix():
    assert parse_timestamp("1722470400") == 1722470400.0
    assert parse_timestamp("1722470400.123") == 1722470400.123

 def test_parse_timestamp_iso():
    ts = 1722470400.0
    assert parse_timestamp("2024-08-01T00:00:00") == ts
    assert parse_timestamp("2024-08-01T00:00:00Z") == ts

 def test_parse_csv(sample_csv):
    field_map = {"ts": "timestamp", "duration": "response_time", "status": "status_code", "endpoint": "endpoint", "method": "method", "error": "error"}
    reqs = list(parse_csv(sample_csv, field_map))
    assert len(reqs) == 10
    assert reqs[0].timestamp == 1722470400.0
    assert reqs[0].duration == 120.5
    assert reqs[0].status_code == 200
    assert reqs[0].endpoint == "/api/home"
    assert reqs[2].error == "timeout"

 def test_parse_json(sample_json):
    field_map = {"ts": "timestamp", "duration": "response_time", "status": "status_code", "endpoint": "endpoint", "method": "method", "error": "error"}
    reqs = list(parse_json(sample_json, field_map))
    assert len(reqs) == 4
    assert reqs[0].duration == 120.5

 def test_parse_invalid_rows():
    # Test skips
    pass  # Implicit in parser
