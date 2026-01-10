import json
from datetime import datetime, timezone

import pytest
from pathlib import Path
from websocket_tester.session import SessionManager, save_session, load_session


@pytest.fixture
def sample_entries():
    return [
        SessionManager.new_entry("out", {"ping": 1}),
        SessionManager.new_entry("in", "pong"),
    ]


def test_new_entry():
    entry = SessionManager.new_entry("out", {"test": True})
    assert entry["direction"] == "out"
    assert "payload" in entry
    assert isinstance(entry["ts"], str)


def test_save_load(tmp_path: Path, sample_entries):
    path = tmp_path / "test.jsonl"
    save_session(sample_entries, path)
    assert path.exists()

    loaded = list(load_session(path))
    assert len(loaded) == 2
    assert loaded[0]["direction"] == "out"
    assert isinstance(loaded[0]["payload"], dict)


def test_load_invalid(tmp_path: Path):
    path = tmp_path / "invalid.jsonl"
    path.write_text("invalid json")
    with pytest.raises(ValueError):
        list(load_session(path))


def test_save_empty(tmp_path: Path):
    path = tmp_path / "empty.jsonl"
    save_session([], path)
    assert path.read_text() == ""
