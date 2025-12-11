'''Integration tests for CLI.''' 

from typer.testing import CliRunner

import curl_to_python.cli


runner = CliRunner()


def test_cli_simple():
    """Test basic CLI invocation."""
    result = runner.invoke(
        curl_to_python.cli.app,
        ["'curl https://example.com'"],
    )
    assert result.exit_code == 0
    assert "import requests" in result.stdout
    assert "https://example.com" in result.stdout


def test_cli_json_post():
    """Test JSON post."""
    curl = "'curl -X POST https://api.com -H \"Content-Type: application/json\" -d '{\\\"a\":1}''"
    result = runner.invoke(curl_to_python.cli.app, [curl])
    assert result.exit_code == 0
    assert "json={" in result.stdout
    assert "\"a\": 1" in result.stdout


def test_cli_error():
    """Test error handling."""
    result = runner.invoke(curl_to_python.cli.app, ["'invalid'"])
    assert result.exit_code == 1
    assert "Parse error" in result.stderr


def test_cli_async_httpx():
    """Test async httpx."""
    result = runner.invoke(
        curl_to_python.cli.app,
        ["'curl https://ex.com'", "--httpx", "--async"],
    )
    assert result.exit_code == 0
    assert "async with httpx.AsyncClient()" in result.stdout


def test_cli_async_no_httpx():
    """--async requires --httpx."""
    result = runner.invoke(
        curl_to_python.cli.app, ["'curl https://ex.com'", "--async"]
    )
    assert result.exit_code == 2
    assert "--async requires --httpx" in result.stderr
