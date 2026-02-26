import typer
from click.testing import CliRunner
from smart_readme_generator.main import app


runner = CliRunner()


def test_scan_help():
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "Scan project" in result.stdout


def test_generate_help():
    result = runner.invoke(app, ["generate", "--help"])
    assert result.exit_code == 0
    assert "Generate README" in result.stdout
