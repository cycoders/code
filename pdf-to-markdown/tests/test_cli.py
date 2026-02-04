import pytest
from typer.testing import CliRunner
from pdf_to_markdown.__main__ import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_cli_version(monkeypatch):
    monkeypatch.setattr("pdf_to_markdown.__main__.__version__", "0.1.0")
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_cli_no_file(tmp_path):
    result = runner.invoke(app, [str(tmp_path / "missing.pdf")])
    assert result.exit_code == 1
    assert "PDF file not found" in result.stdout