import pytest
from pathlib import Path

@pytest.fixture
def sample_env(tmp_path: Path):
    env = tmp_path / ".env"
    env.write_text("""
DB_HOST=localhost
DB_PORT=5432
DB_URL=postgres://${DB_HOST}:${DB_PORT}/mydb
API_KEY=${SECRET_KEY}
""")
    return env

@pytest.fixture
def sample_compose(tmp_path: Path):
    compose = tmp_path / "docker-compose.yml"
    compose.write_text("""
services:
  app:
    environment:
      DB_URL: postgres://${DB_HOST:-localhost}:5432/db
      DEBUG: ${NODE_ENV:-production}
    env_file: .env
""")
    return compose
