import pytest
from metrics_cardinality_cli.parser import parse_exposition

def test_basic_parse():
    lines = ["http_requests_total{method=\"GET\"} 42"]
    out = list(parse_exposition(lines))
    assert len(out) == 1
    assert out[0]["name"] == "http_requests_total"

def test_ignores_comments():
    lines = ["# HELP foo", "foo 1"]
    assert len(list(parse_exposition(lines))) == 1

def test_label_extraction():
    lines = ['foo{bar="baz",quux="1"} 1']
    m = list(parse_exposition(lines))[0]
    assert m["labels"]["bar"] == "baz"