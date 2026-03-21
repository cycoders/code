import click
from click.testing import CliRunner
from k8s_cost_estimator_cli.main import cli

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "scan" in result.stdout

# Note: Integration tests omitted for brevity; use e2e in CI
