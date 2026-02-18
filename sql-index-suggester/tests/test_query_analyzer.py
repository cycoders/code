import pytest
from sql_index_suggester.query_analyzer import analyze_queries
from sql_index_suggester.schema import extract_schema, Schema


def test_analyze_queries(sample_schema, sample_queries):
    schema = extract_schema(sample_schema, "postgres")
    usages = analyze_queries(sample_queries, "postgres", schema)
    assert usages.query_count == 3
    orders_usage = usages.usages["orders"]
    assert orders_usage.predicates["orders.user_id"] >= 1
    assert orders_usage.predicates["orders.status"] >= 1
