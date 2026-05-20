import pytest
from thread_safety_linter.analyzer import analyze_path

def test_detects_threading_usage(tmp_path):
    f = tmp_path / "t.py"
    f.write_text("import threading\nlock = threading.Lock()")
    assert len(analyze_path(str(tmp_path))) > 0

def test_ignores_non_thread_code(tmp_path):
    f = tmp_path / "clean.py"
    f.write_text("x = 1 + 2")
    assert analyze_path(str(tmp_path)) == []
