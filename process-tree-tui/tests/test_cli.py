import sys
from typer.testing import CliRunner

from process_tree_tui.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "Interactive process tree" in result.stdout


def test_cli_no_args(monkeypatch, mocker):
    """Mock app.run to avoid TUI launch."""
    mocker.patch("process_tree_tui.app.ProcessTreeApp.run")
    result = runner.invoke(app)
    assert result.exit_code == 0


def test_cli_options():
    result = runner.invoke(app, ["--refresh", "1.0", "--search", "test"])
    assert result.exit_code == 0


def test_cli_invalid_option():
    result = runner.invoke(app, ["--invalid"])
    assert result.exit_code != 0
    assert "Error:" in result.stderr