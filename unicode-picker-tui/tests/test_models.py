"""Test UnicodeChar model."""

import unicodedata
from unicode_picker_tui.models import UnicodeChar


def test_from_codepoint():
    char = UnicodeChar.from_codepoint(0x1F600)  # 😀
    assert char.codepoint == "U+1F600"
    assert char.char == "😀"
    assert "GRINNING" in char.name
    assert char.category == "So"
