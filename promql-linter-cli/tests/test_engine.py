import pytest
from promql_linter_cli.engine import lint

def test_empty_rules():
    assert lint('up', []) == []