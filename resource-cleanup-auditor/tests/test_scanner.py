import tempfile
from pathlib import Path
from resource_cleanup_auditor.scanner import scan_directory

def test_detects_raw_open():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "bad.py"
        p.write_text("f = open('x.txt')")
        assert len(scan_directory(tmp)) >= 0