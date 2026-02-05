import pytest
from pathlib import Path
from font_subsetter.extractor import (
    extract_glyphs_from_file,
    extract_html_text,
    extract_js_strings,
    extract_css_strings,
)


def test_extract_html_text(sample_html):
    glyphs = extract_html_text(sample_html)
    assert ord('H') in glyphs
    assert ord('!') in glyphs
    assert ord('м') in glyphs  # Cyrillic
    assert ord('ñ') in glyphs
    assert ord('☃') not in glyphs  # Not in text


def test_extract_js_strings(sample_js):
    glyphs = extract_js_strings(sample_js)
    assert ord('H') in glyphs
    assert ord('☃') in glyphs  # \u2603
    assert ord('`') not in glyphs  # Template quotes excluded


def test_extract_css_strings(sample_css):
    glyphs = extract_css_strings(sample_css)
    assert ord('S') in glyphs
    assert ord('☃') in glyphs


def test_extract_glyphs_from_file(tmp_path, sample_html):
    file_path = tmp_path / "test.html"
    file_path.write_text(sample_html)
    glyphs = extract_glyphs_from_file(file_path)
    assert len(glyphs) > 10
    assert ord('W') in glyphs


def test_nonexistent_file():
    glyphs = extract_glyphs_from_file(Path("nonexistent.html"))
    assert glyphs == set()


def test_filter_control_chars():
    content = "\n\tHello\u0000"
    glyphs = extract_js_strings(f'"{content}"')
    assert ord('\n') not in glyphs
    assert ord('H') in glyphs