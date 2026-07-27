import pytest
from tracecontext_validator.core import parse_traceparent

def test_valid_header():
    ctx = parse_traceparent("00-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01")
    assert ctx.valid is True

def test_invalid_format():
    ctx = parse_traceparent("not-a-header")
    assert ctx.valid is False

def test_reserved_values():
    ctx = parse_traceparent("00-00000000000000000000000000000000-0000000000000000-00")
    assert ctx.valid is False

def test_version_ff():
    ctx = parse_traceparent("ff-0af7651916cd43dd8448eb211c80319c-00f067aa0ba902b7-01")
    assert ctx.valid is False

def test_edge_parent_id():
    ctx = parse_traceparent("00-0af7651916cd43dd8448eb211c80319c-0000000000000000-01")
    assert ctx.valid is False