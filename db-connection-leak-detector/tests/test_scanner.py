import tempfile
from pathlib import Path
from db_connection_leak_detector.scanner import scan_path

def test_detects_connect_without_close():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "bad.py"
        p.write_text("conn = engine.connect()\n# no close")
        assert len(scan_path(tmp)) == 1

def test_ignores_safe_pattern():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "good.py"
        p.write_text("with engine.connect() as conn: pass")
        assert len(scan_path(tmp)) == 0

def test_handles_syntax_error():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "broken.py"
        p.write_text("def foo(: pass")
        assert scan_path(tmp) == []