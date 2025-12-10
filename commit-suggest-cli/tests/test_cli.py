import pytest
from typer.testing import CliRunner
from commit_suggest_cli.cli import app

runner = CliRunner()


def test_suggest_help(monkeypatch):
    # Mock to avoid git errors
    monkeypatch.setenv("PWD", "/tmp")
    result = runner.invoke(app, ["suggest", "--help"])
    assert result.exit_code == 0
    assert "Suggest a conventional commit message" in result.stdout


def test_types(monkeypatch):
    result = runner.invoke(app, ["types"])
    assert result.exit_code == 0
    assert "feat, fix" in result.stdout


def test_validate_valid():
    result = runner.invoke(app, ["validate", "feat(ui): ok"])
    assert result.exit_code == 0
    assert "Valid" in result.stdout


def test_validate_invalid():
    result = runner.invoke(app, ["validate", "bad"])
    assert result.exit_code == 1
    assert "Invalid" in result.stdout
