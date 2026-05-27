import pytest
from ulid_toolkit.core import generate, parse, ULID

def test_generate_returns_ulid():
    u = generate()
    assert isinstance(u, ULID)

def test_parse_roundtrip():
    u = generate()
    assert parse(str(u)) == u

def test_str_length():
    u = generate()
    assert len(str(u)) == 32