import pytest
from accept_header_resolver import resolve

def test_basic():
    assert resolve("text/html", ["text/html"]).offered == "text/html"

def test_q_value():
    r = resolve("text/plain;q=0.5, text/html", ["text/html", "text/plain"])
    assert r.offered == "text/html"

def test_wildcard():
    r = resolve("*/*", ["application/json"])
    assert r.offered == "application/json"

def test_no_match():
    assert resolve("text/html", ["application/json"]) is None

def test_precedence():
    r = resolve("application/*, */*", ["text/plain", "application/json"])
    assert r.offered == "application/json"