import typer
test_runner = typer.testing.CliRunner()

from merge_risk_analyzer.cli import app


def test_cli_help(mocker):
    result = test_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Analyze merge risk" in result.stdout


def test_cli_version(mocker):
    result = test_runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout

# Integration smoke test would require full repo mock
