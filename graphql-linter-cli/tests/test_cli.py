import pytest
from click.testing import CliRunner
from graphql_linter_cli.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_lint_good(runner, examples_dir):
    result = runner.invoke(cli, ["lint", str(examples_dir / "good.graphql")])
    assert result.exit_code == 0
    assert "No issues found" in result.stdout


def test_cli_lint_bad(runner, examples_dir):
    result = runner.invoke(cli, ["lint", str(examples_dir / "bad.graphql")])
    assert result.exit_code == 1
    assert "type-pascal-case" in result.stdout
    assert "deprecated-no-reason" in result.stdout


def test_cli_no_paths(runner):
    result = runner.invoke(cli, ["lint"])
    assert result.exit_code == 1