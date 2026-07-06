import ast
from prng_quality_auditor.scanner import scan_path, Finding

def test_detects_random(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text("import random\nrandom.random()")
    res = scan_path(str(tmp_path))
    assert len(res) == 1

def test_ignores_secure(tmp_path):
    f = tmp_path / "good.py"
    f.write_text("import secrets\nsecrets.token_bytes()")
    assert scan_path(str(tmp_path)) == []

def test_reports_line_number(tmp_path):
    f = tmp_path / "x.py"
    f.write_text("import random\nrandom.randint(1, 10)")
    res = scan_path(str(tmp_path))
    assert res[0].line == 2

def test_handles_syntax_error(tmp_path):
    f = tmp_path / "bad.py"
    f.write_text("import random\nrandom.(")
    assert scan_path(str(tmp_path)) == []

def test_multiple_findings(tmp_path):
    f = tmp_path / "m.py"
    f.write_text("import random\nrandom.random()\nrandom.choice([])")
    assert len(scan_path(str(tmp_path))) == 2