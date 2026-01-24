import json
import pytest
from sql_explain_viz.parser import parse_explain
from sql_explain_viz.models import PlanNode


@pytest.fixture
def simple_postgres():
    return '[{"Plan":{"Node Type":"Seq Scan","Total Cost":10.0,"Plan Rows":100}}]'


@pytest.fixture
def nested_postgres():
    return json.dumps({
        "Plan": {
            "Node Type": "Nested Loop",
            "Total Cost": 25.0,
            "Plan Rows": 100,
            "Plans": [{"Node Type": "Seq Scan", "Total Cost": 10.0}]
        }
    })


@pytest.fixture
def simple_sqlite():
    return """QUERY PLAN
|--SCAN TABLE users"""


def test_postgres_simple(simple_postgres):
    node = parse_explain(simple_postgres, "postgres")
    assert node.node_type == "Seq Scan"
    assert node.total_cost == 10.0
    assert node.plan_rows == 100


def test_postgres_nested(nested_postgres):
    node = parse_explain(nested_postgres, "postgres")
    assert node.node_type == "Nested Loop"
    assert len(node.children) == 1
    assert node.children[0].node_type == "Seq Scan"


def test_sqlite_simple(simple_sqlite):
    node = parse_explain(simple_sqlite, "sqlite")
    assert "SCAN TABLE users" in node.node_type


def test_auto_detect_postgres(simple_postgres):
    node = parse_explain(simple_postgres)
    assert isinstance(node, PlanNode)


def test_auto_detect_sqlite(simple_sqlite):
    node = parse_explain(simple_sqlite)
    assert node.node_type == "Query Plan"