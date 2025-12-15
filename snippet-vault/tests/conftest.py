import pytest
from pathlib import Path
from snippet_vault.db import SnippetDB
from snippet_vault.models import Snippet


@pytest.fixture
def test_db_path(tmp_path: Path):
    return tmp_path / "test.db"


@pytest.fixture
def db(test_db_path: Path):
    db = SnippetDB(test_db_path)
    # Seed data
    s1 = Snippet(title="test1", language="python", tags=["test"], content="print(1)")
    db.add(s1)
    s2 = Snippet(title="hello world", language="js", tags=["web"], content="console.log('hi')")
    db.add(s2)
    return db
