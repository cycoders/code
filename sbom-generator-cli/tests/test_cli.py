import json
from typer.testing import CliRunner

from sbom_generator_cli.cli import app

runner = CliRunner()


def test_version(mocker):
    mocker.patch("sys.argv", ["", "--version"])
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Generate SBOM" in result.stdout
