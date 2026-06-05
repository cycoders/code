import tempfile
from pathlib import Path
from context_manager_linter.scanner import scan_directory

def test_detects_bare_open():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "bad.py"
        p.write_text("f = open('x.txt')")
        assert len(scan_directory(tmp)) == 1

def test_ignores_with_statement():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "good.py"
        p.write_text("with open('x.txt') as f: pass")
        assert len(scan_directory(tmp)) == 0

def test_skips_tests():
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "test_bad.py").write_text("f = open('x')")
        assert len(scan_directory(tmp)) == 0