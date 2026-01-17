import pytest
from jsonl_processor.utils import parse_value, apply_op


@pytest.mark.parametrize(
    "inp,exp",
    [
        ('null', None),
        ('true', True),
        ('false', False),
        ('1', 1),
        ('1.5', 1.5),
        ('["a","b"]', ["a", "b"]),
        ('"hello"', "hello"),
    ],
)
def test_parse_value(inp, exp):
    assert parse_value(inp) == exp


@pytest.mark.parametrize(
    "left,right,op,exp",
    [
        (20, 18, ">", True),
        (17, 18, ">", False),
        ("foo", "o", "contains", True),
        ("foo", "x", "contains", False),
        (1, "1", "==", True),
        (1.0, 1, "==", True),
    ],
)
def test_apply_op(left, right, op, exp):
    assert apply_op(left, op, right) == exp


def test_apply_op_type_fail():
    assert not apply_op("a", 1, ">")
    assert not apply_op(None, None, "contains")