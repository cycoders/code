import pytest
from typer.testing import Result
from sql_erd_cli.tests.conftest import cli_runner


def test_cli_help(cli_runner: pytest.FixtureRequest):
    result: Result = cli_runner.invoke(generate)  # Note: typer test via invoke
    assert result.exit_code == 0
    assert "Generate ERD" in result.stdout