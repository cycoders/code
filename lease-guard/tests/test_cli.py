from typer.testing import CliRunner
from lease_guard.cli import app

def test_cli_acquire():
    runner = CliRunner()
    result = runner.invoke(app, ["acquire", "testkey"])
    assert result.exit_code == 0
    assert "acquired" in result.output