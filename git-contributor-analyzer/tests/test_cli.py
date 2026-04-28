import pytest
from click.testing import CliRunner
from git_contributor_analyzer.cli import app


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_help(runner):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Analyze contributor stats" in result.stdout

# Integration via parser/stats tests
