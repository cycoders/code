import pytest
from datetime import datetime
from code_ownership_cli.blame import parse_blame_porcelain

def test_parse_blame_porcelain(mock_blame_output):
    blames = list(parse_blame_porcelain(mock_blame_output))
    assert len(blames) == 2
    author, dt = blames[0]
    assert author == "John Doe"
    assert dt == datetime(2023, 8, 28, 0, 0)


def test_parse_empty():
    assert list(parse_blame_porcelain("")) == []


def test_parse_boundary_only():
    assert list(parse_blame_porcelain("boundary\n")) == []
