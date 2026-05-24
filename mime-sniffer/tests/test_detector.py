import pytest
from pathlib import Path
from mime_sniffer.detector import sniff

def test_pdf_signature(tmp_path):
    p = tmp_path / "x.pdf"
    p.write_bytes(b"%PDF-1.4\n%\xe2")
    assert sniff(p) == "application/pdf"

def test_png_signature(tmp_path):
    p = tmp_path / "x.png"
    p.write_bytes(b"\x89PNG\r\n\x1a\n")
    assert sniff(p) == "image/png"

def test_json_heuristic(tmp_path):
    p = tmp_path / "x.json"
    p.write_bytes(b'{"a":1}')
    assert sniff(p) == "application/json"

def test_unknown_returns_none(tmp_path):
    p = tmp_path / "x.bin"
    p.write_bytes(b"\x00\x01\x02")
    assert sniff(p) is None

def test_stream_interface(tmp_path):
    p = tmp_path / "x.pdf"
    p.write_bytes(b"%PDF-1.4")
    with open(p, "rb") as f:
        assert sniff(f) == "application/pdf"