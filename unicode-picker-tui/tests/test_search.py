"""Test search logic."""

import pytest
from unicode_picker_tui.models import UnicodeChar
from unicode_picker_tui.search import search_chars


@pytest.fixture
def sample_chars():
    return [
        UnicodeChar("U+0041", "A", "LATIN CAPITAL LETTER A", "Lu", "Basic Latin", "L", "N", "", "N"),
        UnicodeChar("U+1F600", "😀", "GRINNING FACE", "So", "Emoticons", "ON", "N", "", "N"),
    ]


def test_search_empty(sample_chars):
    assert search_chars(sample_chars, "") == sample_chars


def test_search_fuzzy(sample_chars):
    results = search_chars(sample_chars, "grin")
    assert len(results) == 1
    assert results[0].name == "GRINNING FACE"


def test_search_threshold(sample_chars):
    results = search_chars(sample_chars, "xyz", threshold=99)
    assert len(results) == 0
