import typer
from typer.testing import CliRunner

from curl_history_analyzer.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout

# Note: Full CLI tests rely on parser/analyzer units; integration via manual


def test_bad_group():
    result = runner.invoke(app, ["--group-by", "invalid"])
    assert result.exit_code == 1
    assert "group-by must be" in result.stdout