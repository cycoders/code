from pathlib import Path

from bidi_text_security_cli.scanner import scan_file

def test_detects_rlo(tmp_path: Path) -> None:
    f = tmp_path / "bad.py"
    f.write_text("x = 1\u202e # hidden")
    findings = list(scan_file(f))
    assert len(findings) == 1
    assert findings[0].name == "RLO"
    assert findings[0].risk == "high"

def test_ignores_clean_file(tmp_path: Path) -> None:
    f = tmp_path / "good.py"
    f.write_text("print('hello')")
    assert list(scan_file(f)) == []


def test_handles_multiple(tmp_path: Path) -> None:
    f = tmp_path / "multi.txt"
    f.write_text("a\u202ab\u202ec")
    assert len(list(scan_file(f))) == 2