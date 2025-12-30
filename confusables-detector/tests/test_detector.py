import pytest
from confusables_detector.detector import is_confusable, get_skeleton, normalize


@pytest.mark.parametrize(
    "char,expected",
    [
        ("a", False),
        ("A", False),
        ("１", True),  # FULLWIDTH DIGIT ONE
        ("ａ", True),  # FULLWIDTH LATIN SMALL LETTER A
        ("а", True),  # CYRILLIC SMALL LETTER A
        ("𝕒", True),  # MATHEMATICAL DOUBLE-STRUCK SMALL A
        ("𝟏", True),
        ("ﬁ", True),  # LATIN SMALL LIGATURE FI
        ("😂", False),  # legit emoji
        ("€", False),
    ],
)
def test_is_confusable(char: str, expected: bool):
    assert is_confusable(char) == expected


@pytest.mark.parametrize(
    "char,expected",
    [
        ("ａ", "a"),
        ("１", "1"),
        ("а", "a"),
        ("ﬁ", "fi"),
    ],
)
def test_get_skeleton(char: str, expected: str):
    assert get_skeleton(char) == expected


@pytest.mark.parametrize(
    "text,expected",
    [
        ("hello ｗorld", "hello world"),
        ("mаin()", "main()"),
        ("fileﬁ.txt", "filefi.txt"),
        ("no change", "no change"),
        ("😂 ok", "😂 ok"),
    ],
)
def test_normalize(text: str, expected: str):
    assert normalize(text) == expected
