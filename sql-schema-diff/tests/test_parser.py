import pytest
from sql_schema_diff.parser import parse_schema
from sql_schema_diff.schema import Column, Table


@pytest.fixture
def simple_sql():
    return """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE
);
    """


def test_parse_simple(tmp_path, simple_sql):
    sql_file = tmp_path / "test.sql"
    sql_file.write_text(simple_sql)
    schema = parse_schema(str(sql_file), "postgres")
    assert len(schema.tables) == 1
    users = schema.tables["users"]
    assert isinstance(users, Table)
    assert users.columns["id"].type_ == "SERIAL"
    assert users.columns["id"].primary_key is True
    assert users.columns["id"].nullable is False
    assert users.columns["name"].nullable is False
    assert users.columns["email"].unique is True


def test_parse_index(tmp_path):
    sql = """
CREATE TABLE users (id SERIAL PRIMARY KEY);
CREATE INDEX idx_email ON users (email);
    """
    sql_file = tmp_path / "test.sql"
    sql_file.write_text(sql)
    schema = parse_schema(str(sql_file), "postgres")
    users = schema.tables["users"]
    assert len(users.indexes) == 1
    assert users.indexes[0].name == "idx_email"


@pytest.mark.parametrize("dialect", ["mysql", "sqlite", "postgres"])
def test_multi_dialect(tmp_path, dialect):
    sql = "CREATE TABLE test (id INT PRIMARY KEY);"
    sql_file = tmp_path / "test.sql"
    sql_file.write_text(sql)
    schema = parse_schema(str(sql_file), dialect)
    assert "test" in schema.tables
