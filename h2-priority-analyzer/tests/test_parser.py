import json
from pathlib import Path

from h2_priority_analyzer.parser import parse_netlog

from .conftest import sample_netlog_path


def test_parse_netlog(sample_netlog_path: Path):
    streams = parse_netlog(sample_netlog_path)
    assert len(streams) >= 1
    s = streams[0]
    assert s.id == 1
    assert s.priority.weight == 201


def test_parse_invalid(tmp_path: Path):
    bad_path = tmp_path / "bad.jsonl"
    bad_path.write_text("invalid json")
    streams = parse_netlog(bad_path)
    assert len(streams) == 0  # graceful


def test_duration_calc():
    path = Path(__file__).parent / "data" / "full-sample.jsonl"
    # Assume sample has start/end
    streams = parse_netlog(path)
    for s in streams:
        assert s.duration is not None
        assert s.duration >= 0
