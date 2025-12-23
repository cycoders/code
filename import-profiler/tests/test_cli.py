from pathlib import Path
from typer.testing import CliRunner
from import_profiler.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Profile" in result.stdout


def test_cli_profile(tmp_script):
    demo_path = tmp_script("import os")
    result = runner.invoke(app, [demo_path])
    assert result.exit_code == 0
    assert "ms" in result.stdout


def test_cli_error():
    result = runner.invoke(app, ["nonexistent.py"])
    assert result.exit_code == 1
    assert "Error" in result.stdout
