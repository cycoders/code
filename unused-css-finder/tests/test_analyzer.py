import pytest
from pathlib import Path
from bs4 import BeautifulSoup
from cssutils import CSSParser, CSSRule

from unused_css_finder.analyzer import (
    load_html_files,
    analyze_css_file,
    get_all_style_rules,
    purge_used_css,
)


@pytest.fixture
def simple_html():
    return BeautifulSoup("<html><body><p class=\"foo\">hi</p></body></html>", "lxml")


@pytest.fixture
def simple_css():
    parser = CSSParser()
    return parser.parseString(".foo { color: red; } .bar { display: none; }")


def test_get_all_style_rules(simple_css):
    rules = get_all_style_rules(simple_css)
    assert len(rules) == 2
    assert rules[0].selectorText == ".foo"


def test_analyze_used(simple_html, simple_css):
    results = []
    style_rules = get_all_style_rules(simple_css)
    # Manual simulate
    for rule in style_rules:
        used = simple_html.select(rule.selectorText)
        results.append({"used": bool(used)})
    assert results[0]["used"] is True
    assert results[1]["used"] is False


def test_analyze_css_file(temp_html_css):
    html_file, css_file = temp_html_css
    soups = load_html_files([Path(html_file)])
    assert len(soups) == 1
    results = analyze_css_file(css_file, soups)
    used_selectors = [r["selector"] for r in results if r["used"]]
    unused_selectors = [r["selector"] for r in results if not r["used"]]
    assert ".used" in used_selectors
    assert ".unused" in unused_selectors
    assert len(results) >= 3  # + nested


def test_purge_used_css(temp_html_css):
    html_file, css_file = temp_html_css
    soups = load_html_files([Path(html_file)])
    results = analyze_css_file(css_file, soups)
    out_path = Path(temp_html_css[0]).with_name("purged.css")
    purge_used_css(results, out_path)
    assert out_path.exists()
    content = out_path.read_text()
    assert ".used" in content
    assert ".unused" not in content


def test_load_html_files(tmp_path):
    (tmp_path / "page.html").write_text("<html></html>")
    (tmp_path / "sub" / "page2.htm").mkdir(parents=True)
    (tmp_path / "sub" / "page2.htm").write_text("<html></html>")
    files = load_html_files([tmp_path])
    assert len(files) == 2