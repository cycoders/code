import typer
from typer.testing import CliRunner
from py_leak_detector.cli import app

runner = CliRunner()


def test_monitor_help():
    result = runner.invoke(app, ["monitor", "--help"])
    assert result.exit_code == 0
    assert "Monitor script for leaks." in result.stdout


def test_monitor_no_script():
    result = runner.invoke(app, ["monitor"])
    assert result.exit_code != 0
    assert "Missing argument" in result.stdout
