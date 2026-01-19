import pytest
from pathlib import Path

import sql_erd_cli.parser as parser
from sql_erd_cli.models import Schema, Table, Column


@pytest.fixture
def sample_sql():
    return """
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100)
);

CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id)
);
    """


def test_parse_basic(sample_sql):
    schema = parser.parse_schema(sample_sql, "postgres")
    assert isinstance(schema, Schema)
    assert len(schema.tables) == 2
    users = schema.tables["users"]
    assert isinstance(users, Table)
    assert "id" in users.columns
    assert users.columns["id"].pk is True
    assert users.columns["id"].type_ == "serial"


def test_parse_fk(sample_sql):
    schema = parser.parse_schema(sample_sql, "postgres")
    posts = schema.tables["posts"]
    assert posts.columns["user_id"].fkey == "users.id"


def test_empty_sql():
    schema = parser.parse_schema("", "postgres")
    assert len(schema.tables) == 0


def test_invalid_sql():
    with pytest.raises(ValueError):
        parser.parse_schema("SELECT 1", "postgres")