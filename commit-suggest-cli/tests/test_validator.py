import pytest
from commit_suggest_cli.validator import validate_commit


def test_valid():
    msg = "feat(ui): add button"
    valid, issues = validate_commit(msg)
    assert valid
    assert issues == []


def test_valid_with_scope():
    valid, _ = validate_commit("fix(parser): handle edge case")
    assert valid


def test_invalid_format():
    valid, issues = validate_commit("invalid")
    assert not valid
    assert "Invalid format" in issues[0]


def test_too_long_subject():
    long = "feat(ui): " + "a" * 80
    valid, issues = validate_commit(long)
    assert not valid
    assert "Subject >72 chars" in issues


def test_body_too_long():
    msg = "feat: ok\n" + "a" * 101
    valid, issues = validate_commit(msg)
    assert not valid
    assert ">100 chars" in issues[0]


def test_empty():
    valid, issues = validate_commit("")
    assert not valid
    assert "Empty message" in issues[0]
