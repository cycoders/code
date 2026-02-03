import pytest
from sitemap_auditor_cli.robots import parse_robots


def test_star_disallow_single():
    text = "User-agent: *\nDisallow: /admin/"
    assert parse_robots(text) == ["/admin/"]


def test_multiple_disallows_star():
    text = "User-agent: *\nDisallow: /a/\nDisallow: /b/"
    assert parse_robots(text) == ["/a/", "/b/"]


def test_no_star_section():
    text = "User-agent: BadBot\nDisallow: /\nUser-agent: *\nAllow: /"
    assert parse_robots(text) == []  # No disallow in * section


def test_empty_robots():
    assert parse_robots("") == []


def test_complex_robots():
    text = """User-agent: *
Allow: /
Disallow: /private/
Disallow: /tmp/
User-agent: Googlebot
Disallow: /no-google/"""
    assert parse_robots(text) == ["/private/", "/tmp/"]