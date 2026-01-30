import pytest
from datetime import datetime, timedelta

from log_to_sequence.parser import parse_log_file
from log_to_sequence.models import Config


def test_parse_valid(sample_jsonl):
    traces = parse_log_file(sample_jsonl, Config())
    assert len(traces) == 2
    assert "t1" in traces
    assert len(traces["t1"]) == 2
    e1 = traces["t1"][0]
    assert e1.service == "frontend"
    assert e1.name == "handle"
    assert e1.duration_ms == 100
    # Sorted
    assert traces["t1"][0].timestamp < traces["t1"][1].timestamp


def test_skip_invalid(tmp_path):
    p = tmp_path / "invalid.jsonl"
    p.write_text('{"invalid": true}\n{"timestamp": "bad"}')
    traces = parse_log_file(p, Config())
    assert traces == {}