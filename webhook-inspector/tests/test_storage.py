import json
from datetime import datetime
from pathlib import Path

from webhook_inspector.storage import Storage


def test_save_and_get(tmp_path: Path):
    storage = Storage(tmp_path)
    req_id = "test123"
    data = {"foo": "bar"}
    storage.save(req_id, data)

    retrieved = storage.get(req_id)
    assert retrieved["foo"] == "bar"
    assert "timestamp" in retrieved


def test_stats(tmp_path: Path):
    storage = Storage(tmp_path)
    storage.save("1", {"signature_verified": True})
    storage.save("2", {})
    stats = storage.stats()
    assert stats["total"] == 2
    assert stats["verified"] == 1


def test_list(tmp_path: Path):
    storage = Storage(tmp_path)
    storage.save("1", {"a": 1})
    storage.save("2", {"b": 2})
    recent = storage.list(1)
    assert len(recent) == 1
    assert recent[0]["b"] == 2
