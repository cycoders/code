import pytest
from click.testing import CliRunner
from py_api_diff.cli import app


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_help(runner):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Detect breaking API changes" in result.stdout

# Integration requires git mock, skipped for unit focus