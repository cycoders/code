import pytest
from sql_index_suggester.index_suggester import generate_suggestions
from sql_index_suggester.query_analyzer import analyze_queries
from sql_index_suggester.schema import extract_schema


def test_generate_suggestions(sample_schema, sample_queries):
    schema = extract_schema(sample_schema, "postgres")
    usages = analyze_queries(sample_queries, "postgres", schema)
    suggestions = generate_suggestions(schema, usages)
    assert len(suggestions) > 0
    assert any("email" in s.columns for s in suggestions)
    high_score = next(s for s in suggestions if s.score >= 20)
    assert "CREATE INDEX" in high_score.sql
