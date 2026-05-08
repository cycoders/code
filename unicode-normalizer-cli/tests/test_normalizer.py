import unicodedata
from unicode_normalizer_cli.normalizer import needs_normalization


def test_needs_normalization_nfc():
    decomposed = "caf\u0301e"  # c a ´ e
    needs, norm = needs_normalization(decomposed, "NFC")
    assert needs is True
    assert norm == "café"


def test_already_normalized():
    composed = "café"
    needs, norm = needs_normalization(composed, "NFC")
    assert needs is False
    assert norm == composed


def test_empty_string():
    needs, norm = needs_normalization("", "NFC")
    assert needs is False


def test_invalid_form():
    with pytest.raises(ValueError):
        needs_normalization("test", "INVALID")