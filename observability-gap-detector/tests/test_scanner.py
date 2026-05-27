import pytest
from observability_gap_detector.scanner import scan_codebase

def test_detects_missing_tracing(tmp_path):
    f = tmp_path / "app.py"
    f.write_text("def handler(): pass")
    gaps = scan_codebase(str(tmp_path))
    assert any("Missing tracing" in g for g in gaps)