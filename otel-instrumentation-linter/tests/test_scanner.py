import tempfile
from pathlib import Path
from otel_instrumentation_linter.scanner import scan_path

def test_detects_missing_span():
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "bad.py"
        p.write_text("import requests\nrequests.get('https://example.com')")
        findings = scan_path(tmp)
        assert len(findings) == 1