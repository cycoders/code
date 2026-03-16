import pytest
from slowlog_analyzer_cli.suggester import suggest


def test_suggestions_select_no_where():
    sugs = suggest("SELECT * FROM users")
    assert any("Missing WHERE" in s for s in sugs)


def test_suggestions_like():
    sugs = suggest("SELECT * FROM users WHERE name LIKE '%foo%'")
    assert any("LIKE" in s for s in sugs)


def test_no_sugs_simple():
    sugs = suggest("SELECT id FROM users WHERE id = ? LIMIT 10")
    assert len(sugs) == 0
