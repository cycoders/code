import pytest
from typer.testing import CliRunner
from http_signer_cli.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_aws4_minimal(monkeypatch):
    monkeypatch.setenv("NO_PYPERCLIP", "1")  # Skip clipboard
    result = runner.invoke(
        app,
        [
            "aws4",
            "sign",
            "--access-key", "AKIA",
            "--secret-key", "key",
            "--region", "us-east-1",
            "--service", "sts",
            "GET",
            "https://sts.amazonaws.com/",
        ],
    )
    assert result.exit_code == 0
    assert "curl" in result.stdout
    assert "Signed cURL" in result.stdout


def test_oauth1_minimal(monkeypatch):
    monkeypatch.setenv("NO_PYPERCLIP", "1")
    result = runner.invoke(
        app,
        [
            "oauth1",
            "sign",
            "--consumer-key", "ck",
            "--consumer-secret", "cs",
            "GET",
            "https://api.example.com/",
        ],
    )
    assert result.exit_code == 0
    assert "OAuth " in result.stdout


def test_missing_args_aws4():
    result = runner.invoke(app, ["aws4", "sign", "GET", "https://example.com"])
    assert result.exit_code != 0
    assert "Error: Missing" in result.stdout
