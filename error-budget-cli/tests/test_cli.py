from click.testing import CliRunner
from error_budget_cli.cli import cli

def test_compute_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["compute", "--target", "99.9", "--total", "100000", "--bad", "30"])
    assert result.exit_code == 0
    assert "Remaining error budget" in result.output