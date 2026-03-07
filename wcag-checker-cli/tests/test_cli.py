import typer
from typer.testing import CliRunner
from wcag_checker_cli.main import app

runner = CliRunner()


def test_scan_help():
    result = runner.invoke(app, ['scan', '--help'])
    assert result.exit_code == 0
    assert 'Scan for WCAG 2.2' in result.stdout

# Note: Full e2e needs files, mocked here
