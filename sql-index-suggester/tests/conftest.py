import pathlib
import pytest
from typer.testing import CliRunner

import sql_index_suggester.cli

runner = CliRunner()

@pytest.fixture
def sample_schema() -> str:
    return """
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    name VARCHAR(255),
    created_at TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    status VARCHAR(50),
    amount DECIMAL,
    created_at TIMESTAMP
);

CREATE INDEX idx_orders_user ON orders (user_id);
    """

@pytest.fixture
def sample_queries() -> str:
    return """
SELECT * FROM users WHERE email = 'test@example.com' ORDER BY created_at;
SELECT * FROM orders WHERE user_id = 1 AND status = 'pending' ORDER BY created_at DESC;
SELECT status, COUNT(*) FROM orders WHERE created_at > '2023-01-01' GROUP BY status;
    """