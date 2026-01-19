import pytest
from sql_erd_cli.models import Schema, Table, Column
from sql_erd_cli.graph_generator import generate_erd
import graphviz


@pytest.fixture
def sample_schema():
    schema = Schema()
    users = Table("users", {"id": Column("id", "serial", pk=True)})
    posts = Table("posts", {"id": Column("id", "serial", pk=True), "user_id": Column("user_id", "int", fkey="users.id")})
    schema.tables["users"] = users
    schema.tables["posts"] = posts
    return schema


def test_generate_erd(sample_schema):
    dot = generate_erd(sample_schema)
    assert isinstance(dot, graphviz.Digraph)
    assert len(dot.body) > 0  # Has nodes/edges
    assert "users" in dot.body
    assert "posts" in dot.body