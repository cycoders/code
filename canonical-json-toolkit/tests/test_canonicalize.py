import pytest
from canonical_json_toolkit.canonicalize import canonicalize, verify

def test_key_order():
    assert canonicalize({"b":1,"a":2}) == '{"a":2,"b":1}'

def test_nested():
    data = {"z":{"y":1,"x":2},"a":[]}
    assert canonicalize(data) == '{"a":[],"z":{"x":2,"y":1}}'

def test_reject_nan():
    with pytest.raises(ValueError):
        canonicalize({"v": float('nan')})

def test_verify():
    assert verify({"a":1}, {"a":1})
    assert not verify({"a":1}, {"a":2})

def test_unicode():
    assert canonicalize({"é": " café"}) == '{"é":" café"}'