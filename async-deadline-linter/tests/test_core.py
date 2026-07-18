import pytest
from async_deadline_linter.core import analyze

def test_detects_missing_deadline(tmp_path):
    f = tmp_path / "t.py"
    f.write_text("async def f(): await g()")
    assert len(analyze(str(tmp_path))) == 1