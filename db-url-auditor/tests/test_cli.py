from click.testing import CliRunner
from db_url_auditor.cli import cli

def test_cli_basic():
    runner = CliRunner()
    result = runner.invoke(cli, ["postgresql://host/db"])
    assert result.exit_code == 0