from typer.testing import CliRunner
from auto_changelog.cli import app


runner = CliRunner()


def test_version_callback(monkeypatch):
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "v0.1.0" in result.stdout


def test_help(mocker):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Generate changelog" in result.stdout


def test_generate_help():
    result = runner.invoke(app, ["generate", "--help"])
    assert result.exit_code == 0
    assert "--since" in result.stdout