import typer
from pathlib import Path
from typer.testing import CliRunner

from h2_priority_analyzer.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Analyze" in result.stdout


def test_cli_invalid_file(tmp_path):
    result = runner.invoke(app, ["analyze", str(tmp_path / "nope.jsonl")])
    assert result.exit_code == 2
    assert "File not found" in result.stdout

# Integration with sample would need patching print
