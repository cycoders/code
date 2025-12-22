import pytest
from query_doctor_cli.optimizer import parse_schema, diagnose
from query_doctor_cli.types import TableSchema
from pathlib import Path
import sqlglot

@pytest.fixture
def sample_schema() -> str:
    return """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    name VARCHAR(100)
);
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    amount DECIMAL
);
CREATE INDEX idx_orders_user_id ON orders(user_id);
"""

@pytest.fixture
def sample_tables(sample_schema: str) -> dict:
    return parse_schema(sample_schema, "postgres")

class TestParseSchema:
    def test_parses_table_columns_and_pk(self, sample_schema: str):
        tables = parse_schema(sample_schema, "postgres")
        users = tables["users"]
        assert users["columns"]["id"] == "serial"
        assert users["columns"]["email"] == "varchar(255)"
        assert "id" in users["indexed_columns"]
        assert "email" not in users["indexed_columns"]

    def test_parses_indexes(self, sample_schema: str):
        tables = parse_schema(sample_schema, "postgres")
        orders = tables["orders"]
        assert "user_id" in orders["indexed_columns"]

    def test_empty_schema(self):
        tables = parse_schema("", "postgres")
        assert tables == {}

class TestDiagnose:
    def test_select_star(self, sample_tables):
        query = "SELECT * FROM users;"
        issues = diagnose(sample_tables, query, "postgres")
        assert any(i["type_"] == "select_star" for i in issues)

    def test_missing_index_filter(self, sample_tables):
        query = "SELECT id FROM users WHERE email = 'test@example.com';"
        issues = diagnose(sample_tables, query, "postgres")
        missing_email = next((i for i in issues if "email" in i["description"]), None)
        assert missing_email is not None
        assert missing_email["severity"] == "high"

    def test_cartesian_product(self, sample_tables):
        query = "SELECT * FROM users, orders;"
        issues = diagnose(sample_tables, query, "postgres")
        assert any(i["type_"] == "cartesian_product" for i in issues)

    def test_no_limit(self, sample_tables):
        query = "SELECT id FROM users;"
        issues = diagnose(sample_tables, query, "postgres")
        assert any(i["type_"] == "no_limit" for i in issues)

    def test_join_missing_index(self, sample_tables):
        query = """
        SELECT o.id FROM orders o
        JOIN users u ON o.user_id = u.email;  -- bad join col
        """.strip()
        issues = diagnose(sample_tables, query, "postgres")
        assert any("JOIN on orders.user_id" in i["description"] for i in issues)  # user_id indexed, but test logic

    def test_no_issues(self, sample_tables):
        query = "SELECT u.id FROM users u WHERE u.id = 1 LIMIT 10;"
        issues = diagnose(sample_tables, query, "postgres")
        assert len(issues) == 1  # select no *, but limit ok, id indexed
