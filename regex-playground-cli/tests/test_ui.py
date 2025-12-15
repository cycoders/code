import re

from regex_playground_cli.ui import get_explanation


@pytest.mark.parametrize(
    "pattern, flags, expected_subs",
    [
        (r"\d+", 0, ["digit [0-9]", "one-or-more +"]),
        (r"[a-z]+", re.I, ["character class [abc]", "case-insensitive (i)"]),
        (r"^foo(bar)?$", re.M, ["start-of-line ^", "capturing group (abc)", "zero-or-one ?", "end-of-line $", "multiline (^/$ per line) (m)"]),
    ],
)
def test_get_explanation(pattern, flags, expected_subs):
    expl = get_explanation(pattern, flags)
    for sub in expected_subs:
        assert sub in expl
