import pytest
import re

from regex_playground_cli.core import RegexTester, MatchResult


@pytest.mark.parametrize(
    "input_str, expected_pattern, expected_flags",
    [
        ("hello", "hello", 0),
        ("/hello/", "hello", 0),
        ("/hello/i", "hello", re.I),
        ("/hello/mi", "hello", re.I | re.M),
        ("(\d+)/i", "(\d+)", re.I),
        ("/^foo$/m", "^foo$", re.M),
    ],
)
def test_from_input_valid(input_str, expected_pattern, expected_flags):
    tester = RegexTester.from_input(input_str)
    assert tester.pattern == expected_pattern
    assert tester.flags_int == expected_flags


@pytest.mark.parametrize(
    "input_str",
    [
        "/",
        "[a-z",
        "/un/knownflag",
    ],
)
def test_from_input_invalid(input_str):
    with pytest.raises(ValueError, match="Invalid regex|Unknown flag"):
        RegexTester.from_input(input_str)


def test_test_no_groups():
    tester = RegexTester.from_input(r"\d+")
    matches = tester.test("abc 123 def 456 ghi")
    assert len(matches) == 3
    assert matches[0] == MatchResult(4, 7, ())
    assert matches[1] == MatchResult(12, 15, ())
    assert matches[2] == MatchResult(20, 23, ())


def test_test_with_groups():
    tester = RegexTester.from_input(r"(\d)(\w+)")
    matches = tester.test("a1b 2c3d 4e")
    assert len(matches) == 3
    assert matches[0].groups == ("1", "b")
    assert matches[1].groups == ("2", "c3d")
    assert matches[2].groups == ("4", "e")


def test_flags_multiline():
    tester = RegexTester.from_input(r"^(\d+)$", "m")
    text = "foo\n123\n456\nbar"
    matches = tester.test(text)
    assert len(matches) == 2
    assert matches[0].groups == ("123",)
    assert matches[1].groups == ("456",)


def test_empty_text():
    tester = RegexTester.from_input(r"a+")
    matches = tester.test("")
    assert len(matches) == 0


def test_no_match():
    tester = RegexTester.from_input(r"xyz")
    matches = tester.test("abc")
    assert len(matches) == 0
