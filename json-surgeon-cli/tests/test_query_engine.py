import pytest
from json_surgeon_cli.query_engine import apply_jmespath


def test_apply_jmespath_simple():
    data = {"users": [{"name": "Alice"}]}
    result = apply_jmespath(data, "users[0].name")
    assert result == "Alice"


def test_apply_jmespath_filter():
    data = {"users": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 20}]}
    result = apply_jmespath(data, "users[?age > 25].name")
    assert result == ["Alice"]


def test_empty_query():
    data = {"a": 1}
    assert apply_jmespath(data, "") == data


def test_invalid_query():
    with pytest.raises(Exception):
        apply_jmespath({}, "non.existent")
