import pytest
from hash_identifier_cli.identifier import identify, _normalize_hex


def test_normalize_hex_valid():
    assert _normalize_hex("5D41402ABC4B2B76B8DB0AEDD4BF355D") == "5d41402abc4b2b76b8db0aedd4bf355d"


def test_normalize_hex_invalid_char():
    with pytest.raises(ValueError, match="valid hexadecimal"):
        _normalize_hex("5d41402g")


def test_normalize_hex_odd_length():
    with pytest.raises(ValueError, match="even length"):
        _normalize_hex("5d41402abc4b2b76b8db0aedd4bf355")


def test_md5_identify(sample_md5):
    results = identify(sample_md5)
    assert len(results) >= 1
    assert results[0]["name"] == "MD5"


def test_sha256_identify(sample_sha256):
    results = identify(sample_sha256)
    assert any(r["name"] == "SHA-256" for r in results)


def test_unknown_length():
    assert identify("a" * 2) == []  # len=1 byte unknown


def test_empty_hex():
    assert identify("") == []


def test_all_candidates(sample_sha256):
    results = identify(sample_sha256, show_all=True)
    assert len(results) > 1  # Multiple for len=64