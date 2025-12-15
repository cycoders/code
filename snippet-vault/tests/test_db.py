import pytest
from datetime import datetime, timedelta
from snippet_vault.db import SnippetDB
from snippet_vault.models import Snippet


def test_add_get(db):
    snippet = Snippet(
        title="new test", language="py", tags=["new"], content="def foo(): pass"
    )
    sid = db.add(snippet)
    assert sid > 0
    fetched = db.get(sid)
    assert fetched.id == sid
    assert fetched.title == "new test"
    assert fetched.content == "def foo(): pass"
    assert fetched.tags == ["new"]
    assert isinstance(fetched.created_at, datetime)


def test_update(db):
    snippet = db.get(1)  # test1
    snippet.title = "updated"
    snippet.tags.append("updated")
    db.update(snippet)
    fetched = db.get(1)
    assert fetched.title == "updated"
    assert "updated" in fetched.tags
    assert fetched.updated_at > snippet.created_at - timedelta(seconds=1)


def test_delete(db):
    sid = 1
    assert db.delete(sid)
    assert db.get(sid) is None
    assert not db.delete(sid)  # already gone
