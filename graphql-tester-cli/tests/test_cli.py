import json
from typer.testing import CliRunner

from graphql_tester_cli.cli import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_query_invalid_json() -> None:
    result = runner.invoke(app, ["query", "https://test.com", "{ test }", "--variables", "{invalid"])
    assert result.exit_code == 1
    assert "Invalid JSON" in result.stderr


def test_history_empty(monkeypatch) -> None:
    # Mock history_mgr.list_recent to []
    def mock_list(*args, **kwargs):
        return []
    monkeypatch.setattr("graphql_tester_cli.history.HistoryManager.list_recent", mock_list)
    result = runner.invoke(app, ["history"])
    assert result.exit_code == 0
