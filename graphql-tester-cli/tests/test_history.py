import pytest
import json
import tempfile
from pathlib import Path

from graphql_tester_cli.history import HistoryManager


@pytest.fixture
def temp_history():
    data_dir = Path(tempfile.mkdtemp())
    mgr = HistoryManager()
    mgr.db_path = data_dir / "test.db"  # patch path
    mgr.data_dir = data_dir
    mgr._init_db()
    yield mgr
    # cleanup implicit


def test_save_and_list_recent(temp_history):
    mgr = temp_history
    mgr.save("https://test.com", "{ test }", {"var": 1}, {"data": {"ok": True}})
    items = mgr.list_recent(5)
    assert len(items) == 1
    assert items[0]["endpoint"].startswith("https://test.com")
    assert items[0]["query"] == "{ test }"


def test_get_nonexistent(temp_history):
    assert temp_history.get(999) is None


def test_get_valid(temp_history):
    mgr = temp_history
    mgr.save("https://test.com", "{ test }", {"var": 1}, {"data": {"ok": True}})
    item = mgr.list_recent(1)[0]
    full_item = mgr.get(item["id"])
    assert full_item["variables"] == {"var": 1}
    assert full_item["result"] == {"data": {"ok": True}}
