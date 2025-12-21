import typer
from typer.testing import CliRunner
from code_ownership_cli.cli import app

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Analyze" in result.stdout

# Integration mock heavy, but core covered

def test_analyze_no_repo(mocker):
    mocker.patch("pathlib.Path.exists", return_value=False)
    result = runner.invoke(app, ["analyze"], standalone_mode=False)
    assert "Not a git repo" in str(result.exception)
