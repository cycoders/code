import tempfile
from pathlib import Path
from crypto_agility_scanner.scanner import scan_path

def test_detects_md5():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "t.py"
        p.write_text("import hashlib\nhashlib.md5(b'data')")
        findings = scan_path(tmp)
        assert len(findings) == 1
        assert findings[0].algorithm == "md5"