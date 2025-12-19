import pytest
from json_surgeon_cli.utils import truncate, update_json_at_path


def test_truncate():
    assert truncate("short") == "short"
    assert truncate("a" * 50, 10) == "a" * 7 + "..."


def test_update_json_at_path():
    data = {"users": [{"name": "Alice", "age": 30}]}
    update_json_at_path(data, ["users", 0, "age"], 31)
    assert data["users"][0]["age"] == 31

    d2 = {"nested": {"list": [1, {"key": "val"}]}}
    update_json_at_path(d2, ["nested", "list", 1, "key"], "new")
    assert d2["nested"]["list"][1]["key"] == "new"
