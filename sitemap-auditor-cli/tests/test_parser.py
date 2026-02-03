import pytest
from sitemap_auditor_cli.parser import get_locs_from_xml


def test_urlset_single_loc():
    xml = b'''<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"><url><loc>https://ex.com/page</loc></url></urlset>'''
    locs = get_locs_from_xml(xml)
    assert locs == ["https://ex.com/page"]


def test_sitemapindex_sub():
    xml = b'''<sitemapindex xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"><sitemap><loc>https://ex.com/sub.xml</loc></sitemap></sitemapindex>'''
    locs = get_locs_from_xml(xml)
    assert locs == ["https://ex.com/sub.xml"]


def test_mixed_locs():
    xml = b'''<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"><loc>https://ex.com/a</loc><loc>https://ex.com/b</loc></urlset>'''
    locs = get_locs_from_xml(xml)
    assert len(locs) == 2
    assert "https://ex.com/a" in locs


def test_invalid_xml():
    xml = b"<invalid></>"
    locs = get_locs_from_xml(xml)
    assert locs == []


def test_no_locs():
    xml = b'<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\"/>'
    locs = get_locs_from_xml(xml)
    assert locs == []