import pytest
from jinja2_security_linter.scanner import scan_directory

def test_detects_unsafe_filter(tmp_path):
    (tmp_path / "bad.j2").write_text("{{ user_input|safe }}")
    findings = scan_directory(str(tmp_path))
    assert len(findings) == 1
    assert findings[0].rule == "unsafe-filter"