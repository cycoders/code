import typer.testing
from deadcode_hunter.cli import app


runner = typer.testing.CliRunner()


def test_scan_help():
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "Scan for deadcode" in result.stdout

# Integration tests would mock finder/analyzer, but CLI parses correctly
