import pytest
from sql_schema_diff.differ import diff_schemas, DiffResult
from sql_schema_diff.schema import Schema, Table, Column


@pytest.fixture
def old_schema():
    schema = Schema(dialect="postgres")
    schema.tables["users"] = Table(
        name="users",
        columns={
            "id": Column("id", "SERIAL", primary_key=True),
            "name": Column("name", "VARCHAR(255)", nullable=False),
        },
    )
    return schema


@pytest.fixture
def new_schema(old_schema):
    schema = Schema(dialect="postgres")
    schema.tables["users"] = Table(
        name="users",
        columns={
            "id": Column("id", "SERIAL", primary_key=True),
            "name": Column("name", "VARCHAR(255)"),
            "age": Column("age", "INTEGER"),
        },
    )
    schema.tables["new_table"] = Table(name="new_table")
    return schema


def test_diff_no_change(old_schema):
    diff = diff_schemas(old_schema, old_schema)
    assert diff == DiffResult({}, {}, {})


def test_diff_changes(old_schema, new_schema):
    diff = diff_schemas(old_schema, new_schema)
    assert "new_table" in diff.added_tables
    assert len(diff.changed_tables) == 1
    changes = diff.changed_tables["users"]
    assert "added_columns" in changes
    assert changes["added_columns"] == ["age"]
    assert "changed_columns" in changes
    assert "name" in changes["changed_columns"]


def test_diff_removed(old_schema, new_schema):
    del new_schema.tables["users"]
    diff = diff_schemas(old_schema, new_schema)
    assert "users" in diff.removed_tables
