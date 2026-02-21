import pytest
from typer.testing import CliRunner
from sql_transpiler_cli.main import app

runner = CliRunner()

@pytest.fixture
def cli_runner():
    return runner

@pytest.fixture
def sample_sql(tmp_path):
    p = tmp_path / "test.sql"
    p.write_text("SELECT * FROM users WHERE id = 1;")
    return p