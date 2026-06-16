import pytest

def test_missing_plan_key():
    with pytest.raises(KeyError):
        from query_plan_diff_cli.parser import parse_explain
        parse_explain('[{}]')