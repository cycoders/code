import pytest
from code_ownership_cli.stats import OwnershipStats
from code_ownership_cli.blame import LineBlame

def test_from_blame_empty():
    stats = OwnershipStats.from_blame([])
    assert stats.total_lines == 0


def test_from_blame_single():
    data: List[LineBlame] = [("Alice", datetime.now())]
    stats = OwnershipStats.from_blame(data)
    assert stats.total_lines == 1
    assert stats.author_lines["Alice"] == 1
    assert len(stats.top_authors) == 1
    assert stats.top_authors[0][1] == 100.0


def test_top_limited():
    data = [("A", datetime.now()), ("B", datetime.now()), ("A", datetime.now())]
    stats = OwnershipStats.from_blame(data)
    assert len(stats.top_authors) == 2
