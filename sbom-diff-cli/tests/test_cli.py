from typer.testing import CliRunner
from sbom_diff_cli.cli import app

runner = CliRunner()

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0