import pytest
from confusables_detector.highlighter import highlight_line
from confusables_detector.detector import is_confusable


@pytest.mark.parametrize(
    "line,exp_count",
    [
        ("hello", 0),
        ("hello ａ!", 1),
        ("mаin", 1),
        ("ﬁle name", 2),
    ],
)
def test_highlight_line(line: str, exp_count: int):
    highlighted, count = highlight_line(line)
    assert count == exp_count
    assert "[red bold]" in highlighted if exp_count else "[red bold]" not in highlighted


def test_highlight_preserves_length_meaning():
    line = "aｂc"
    highlighted, count = highlight_line(line)
    # Markup added, but chars preserved in count
    assert count == 1
    assert len([c for c in highlighted if c not in "[]/ "]) == len(line)
