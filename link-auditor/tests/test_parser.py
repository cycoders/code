import pytest
from link_auditor.parser import extract_links_from_md, extract_links_from_html, extract_urls_from_sitemap


@pytest.mark.parametrize(
    "content, base, expected",
    [
        ('[Home](https://ex.com/)', None, ["https://ex.com/"]),
        ('[Rel](./page.html)', "https://site/dir/", ["https://site/dir/page.html"]),
        ('[Mail](mailto:test@ex.com)', None, []),
    ],
)
def test_extract_md_links(content, base, expected):
    links = extract_links_from_md(content, base)
    assert set(links) == set(expected)


@pytest.mark.parametrize(
    "html, expected",
    [
        ('<a href="https://ex.com">ok</a>', ["https://ex.com"]),
        ('<a href="mailto:no">no</a>', []),
    ],
)
def test_extract_html_links(html, expected):
    links = extract_links_from_html(html)
    assert set(links) == set(expected)


def test_sitemap():
    xml = '''<?xml version="1.0"?><urlset><url><loc>https://ex.com/1</loc></url><url><loc>https://ex.com/2</loc></url></urlset>'''
    links = extract_urls_from_sitemap(xml)
    assert links == ["https://ex.com/1", "https://ex.com/2"]
