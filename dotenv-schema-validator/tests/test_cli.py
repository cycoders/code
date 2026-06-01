from click.testing import CliRunner
from dotenv_schema_validator.cli import cli

def test_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "validate" in result.output