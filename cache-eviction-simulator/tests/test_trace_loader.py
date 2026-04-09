import json
from pathlib import Path
import pytest

from cache_eviction_simulator.trace_loader import load_trace


@pytest.fixture
def tmp_jsonl(tmp_path: Path):
    p = tmp_path / "test.jsonl"
    p.write_text('{"key":"a","size":100}\n{"key":"b","size":200}\n{"key":"c","size":300}\ninvalid\n{"key":"d", "size":"abc"}\n{"key":"e","size":500}')
    return p


@pytest.fixture
def tmp_csv(tmp_path: Path):
    p = tmp_path / "test.csv"
    p.write_text("key,size\na,100\nb,200\nc,300")
    return p


def test_jsonl(tmp_jsonl):
    accesses = list(load_trace(tmp_jsonl))
    assert len(accesses) == 4
    assert accesses[0] == ("a", 100)
    assert accesses[-1] == ("e", 500)


def test_csv(tmp_csv):
    accesses = list(load_trace(tmp_csv))
    assert len(accesses) == 3
    assert accesses == [("a", 100), ("b", 200), ("c", 300)]


def test_invalid_file(tmp_path):
    p = tmp_path / "test.txt"
    p.touch()
    with pytest.raises(ValueError):
        list(load_trace(p))


def test_empty(tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("")
    assert list(load_trace(p)) == []