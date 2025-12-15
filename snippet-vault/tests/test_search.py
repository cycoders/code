import pytest
from snippet_vault.search import fuzzy_search
from snippet_vault.models import Snippet


@pytest.fixture
def sample_snippets():
    return [
        Snippet(title="hello world", content="print hello", tags=["greet"]),
        Snippet(title="hell world", content="print hell", tags=["greet"]),
        Snippet(title="foo bar", content="baz", tags=["other"]),
    ]


def test_fuzzy_search_match(sample_snippets):
    results = fuzzy_search(sample_snippets, "hel wrld", threshold=70)
    assert len(results) == 2
    titles = [r.title for r in results]
    assert "hell world" in titles
    assert "hello world" in titles


def test_fuzzy_search_no_match(sample_snippets):
    results = fuzzy_search(sample_snippets, "xyz", threshold=70)
    assert len(results) == 0


def test_fuzzy_search_tags(sample_snippets):
    results = fuzzy_search(sample_snippets, "greet", threshold=60)
    assert len(results) == 2
