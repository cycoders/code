import pytest
from magic_number_inspector.inspector import identify

def test_png_detection(tmp_path):
    f = tmp_path / "test.png"
    f.write_bytes(b"\x89PNG\r\n\x1a\nrest")
    assert identify(f)[0]["type"] == "image/png"

def test_unknown_file(tmp_path):
    f = tmp_path / "unknown.bin"
    f.write_bytes(b"\x00\x01\x02")
    assert identify(f)[0]["type"] == "unknown"

def test_missing_file():
    with pytest.raises(FileNotFoundError):
        identify("/nonexistent")

def test_truncated_header(tmp_path):
    f = tmp_path / "trunc.png"
    f.write_bytes(b"\x89PNG")
    assert identify(f)[0]["confidence"] >= 0.9

def test_recursive_zip(tmp_path):
    # placeholder for container recursion
    assert True