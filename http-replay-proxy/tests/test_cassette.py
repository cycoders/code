import pytest
from pathlib import Path
from http_replay_proxy.cassette import load_cassette, append_to_cassette

@pytest.fixture
def tmp_cassette(tmp_path: Path):
    return tmp_path / "test.yaml"

def test_load_nonexistent(tmp_cassette):
    assert load_cassette(str(tmp_cassette)) == []

def test_append_load(tmp_cassette):
    inter = {'request': {'method': 'GET'}, 'response': {}, 'latency': 0.1}
    append_to_cassette(str(tmp_cassette), inter)
    assert load_cassette(str(tmp_cassette)) == [inter]

def test_append_multiple(tmp_cassette):
    inter1 = {'foo': 1}
    inter2 = {'foo': 2}
    append_to_cassette(str(tmp_cassette), inter1)
    append_to_cassette(str(tmp_cassette), inter2)
    assert load_cassette(str(tmp_cassette)) == [inter1, inter2]

def test_load_invalid_yaml(tmp_path: Path):
    p = tmp_path / "invalid.yaml"
    p.write_text("invalid: yaml")
    assert load_cassette(str(p)) == []
