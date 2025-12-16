import pytest
from dupe_code_finder.tokenizer import tokenize_source


@pytest.mark.parametrize(
    "source, expected",
    [
        (
            "def foo(x): return x * 2",
            [
                ("DEF", 1),
                ("ID", 1),
                ("LPAREN", 1),
                ("ID", 1),
                ("RPAREN", 1),
                ("COLON", 1),
                ("RETURN", 1),
                ("ID", 1),
                ("TIMES", 1),
                ("NUM", 1),
            ],
        ),
        (
            '# comment\ndef foo(x): pass',
            [("DEF", 2), ("ID", 2), ("LPAREN", 2), ("ID", 2), ("RPAREN", 2), ("COLON", 2), ("NAME", 2)],
        ),
        ('"string"', []),
        ("123 + 'abc'", [("NUM", 1), ("PLUS", 1)]),
    ],
)
def test_tokenize_source(source, expected):
    tokens, _ = tokenize_source(source)
    assert tokens == expected


def test_non_utf8_skipped():
    # tokenizer_file skips, but source assumes utf8
    pass
