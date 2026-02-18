import pytest
from sql_index_suggester.schema import extract_schema, Schema


def test_extract_schema(sample_schema):
    schema = extract_schema(sample_schema, "postgres")
    assert schema.tables["users"]["email"] == "VARCHAR(255)"
    assert "users" in schema.tables
    assert schema.primary_keys["users"] == ["id"]
    assert len(schema.indexes["orders"]) == 1
