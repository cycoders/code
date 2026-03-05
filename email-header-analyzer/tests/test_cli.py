import typer
from typer.testing import CliRunner
from email_header_analyzer.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Analyze" in result.stdout


def test_cli_bad_file(monkeypatch):
    monkeypatch.setattr("sys.stdin.buffer.read", lambda: b"")
    result = runner.invoke(app, ["analyze", "nonexistent.eml"])
    assert result.exit_code == 1
    assert "Parse error" in result.stderr

# Additional edge: JSON
# Note: requires full deps, skipped for unit
