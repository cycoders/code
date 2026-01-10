import asyncio
from typer.testing import Result

from websocket_tester.cli import app, runner


def test_help():
    result: Result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "shell" in result.stdout
    assert "replay" in result.stdout


def test_shell_help():
    result: Result = runner.invoke(app, ["shell", "--help"])
    assert result.exit_code == 0
    assert "--url" in result.stdout


def test_replay_help():
    result: Result = runner.invoke(app, ["replay", "--help"])
    assert result.exit_code == 0
    assert "session_file" in result.stdout