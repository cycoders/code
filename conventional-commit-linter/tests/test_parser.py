import pytest
from conventional_commit_linter.parser import parse_commit_message, parse_header


@pytest.mark.parametrize(
    "header, expected",
    [
        ("feat: add", {"type": "feat", "scope": None, "breaking": False, "subject": "add"}),
        ("feat(ui): add", {"type": "feat", "scope": "ui", "breaking": False, "subject": "add"}),
        ("fix(api)!: remove", {"type": "fix", "scope": "api", "breaking": True, "subject": "remove"}),
    ],
)
def test_parse_header(header, expected):
    assert parse_header(header) == expected


@pytest.mark.parametrize(
    "msg",
    ["invalid header", "feat", "feat:"],
)
def test_parse_header_invalid(msg):
    with pytest.raises(ValueError):
        parse_header(msg)


@pytest.mark.parametrize(
    "msg, body, footer",
    [
        (
            "feat: add\nbody line",
            "body line",
            {},
        ),
        (
            "fix: ok\n\nBODY\n\nCloses: #123\nBREAKING CHANGE: foo",
            "BODY",
            {"Closes": "#123", "BREAKING CHANGE": "foo"},
        ),
    ],
)
def test_parse_commit_message(msg, body, footer):
    parsed = parse_commit_message(msg)
    assert parsed["body"] == body
    assert parsed["footer"] == footer


def test_parse_empty():
    with pytest.raises(ValueError, match="empty"):
        parse_commit_message("")
