from pathlib import Path
import tempfile

from zero_width_char_scanner.scanner import scan_file


def test_detects_zero_width_space():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("x = 'a\u200b'\n")
        name = f.name
    try:
        results = list(scan_file(Path(name)))
        assert len(results) == 1
        assert results[0]["category"] == "zero_width"
    finally:
        Path(name).unlink()


def test_ignores_normal_text():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello world")
        name = f.name
    try:
        assert list(scan_file(Path(name))) == []
    finally:
        Path(name).unlink()
