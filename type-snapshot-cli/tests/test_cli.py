from typer.testing import CliRunner
from type_snapshot_cli.cli import app

def test_help():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "snapshot" in result.output