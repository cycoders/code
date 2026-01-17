import pytest
import json
from pathlib import Path

@pytest.fixture
def sample_jsonl(tmp_path: Path) -> Path:
    """Sample JSONL with variety."""
    content = '''
{"id":1,"age":25,"region":"US","revenue":100.0,"tags":["a","b"]}
{"id":2,"age":17,"region":"EU","revenue":80.0,"tags":["c"]}
{"id":3,"age":30,"region":"US","revenue":120.0,"tags":["a"]}
{"id":4,"age":16,"region":"EU","revenue":90.0,"tags":["d"]}
{"id":5,"age":22,"region":"ASIA","revenue":null,"tags":[]}
{"malformed":true}
'''
    p = tmp_path / "sample.jsonl"
    p.write_text(content.strip())
    return p

@pytest.fixture
def malformed_jsonl(tmp_path: Path) -> Path:
    p = tmp_path / "malformed.jsonl"
    p.write_text('{"ok":true}\ninvalid json\n{"ok":true}')
    return p