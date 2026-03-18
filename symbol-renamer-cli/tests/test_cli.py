import pytest
from typer.testing import CliRunner

from symbol_renamer_cli.cli import app

runner = CliRunner()


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Rename symbols" in result.stdout


def test_cli_invalid_path(tmp_path: Path) -> None:
    result = runner.invoke(app, ["old", "new", str(tmp_path / "missing")])
    assert result.exit_code == 1
    assert "No Python files found" in result.stdout