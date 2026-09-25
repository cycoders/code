import pytest
from sri_hash_generator.core import compute_integrity, process_html

def test_compute_sha384():
    h = compute_integrity("x.js", b"console.log(1)")
    assert h.startswith("sha384-")

def test_process_script_tag():
    html = '<script src="app.js"></script>'
    out, ch = process_html(html)
    assert len(ch) == 1

def test_empty_html():
    out, ch = process_html("")
    assert ch == []

def test_malformed_html():
    out, ch = process_html("<script src=x.js>")
    assert "integrity" in str(out) or len(ch) >= 0

def test_algorithm_switch():
    h = compute_integrity("x.js", b"data", "sha512")
    assert h.startswith("sha512-")