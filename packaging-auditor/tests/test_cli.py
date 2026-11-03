from typer.testing import CliRunner
from packaging_auditor.cli import app

runner = CliRunner()

def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

def test_run_on_empty(tmp_path):
    result = runner.invoke(app, [str(tmp_path)])
    assert result.exit_code == 1