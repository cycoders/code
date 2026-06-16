import pytest
from query_plan_diff_cli.parser import parse_explain

def test_parse_basic_plan():
    plan = parse_explain('[{"Plan": {"Node Type": "Seq Scan"}}]')
    assert plan['Node Type'] == 'Seq Scan'