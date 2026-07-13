import pytest
from priority_inversion_analyzer.analyzer import analyze_path

def test_detects_simple_lock(tmp_path):
    f = tmp_path / "test.py"
    f.write_text("def foo():\n    lock.acquire()")
    res = analyze_path(str(tmp_path))
    assert len(res) == 1

def test_ignores_non_python(tmp_path):
    (tmp_path / "test.txt").write_text("lock.acquire()")
    assert analyze_path(str(tmp_path)) == []

def test_handles_syntax_error(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text("def broken(:")
    assert analyze_path(str(tmp_path)) == []

def test_threshold_filtering(tmp_path):
    f = tmp_path / "simple.py"
    f.write_text("lock.acquire()")
    res = analyze_path(str(tmp_path), "high")
    assert len(res) == 0 or "locks" in res[0]

def test_multiple_files(tmp_path):
    (tmp_path / "a.py").write_text("lock1.acquire()")
    (tmp_path / "b.py").write_text("lock2.acquire()")
    assert len(analyze_path(str(tmp_path))) == 2