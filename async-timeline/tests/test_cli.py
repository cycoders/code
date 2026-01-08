import pytest
from typer.testing import CliRunner

from async_timeline.cli import app

runner = CliRunner()


def test_run_help():
    result = runner.invoke(app, ["run", "--help"])
    assert result.exit_code == 0
    assert "Instrument and visualize" in result.stdout


def test_run_invalid_script(tmp_path):
    fake_script = tmp_path / "fake.py"
    result = runner.invoke(app, ["run", str(fake_script)])
    assert result.exit_code == 2  # Typer validation
    assert "exists" in result.stderr


def test_run_no_tasks(monkeypatch):
    # Mock runpy to do nothing, no tasks
    monkeypatch.setattr("runpy.run_path", lambda *a, **kw: None)
    monkeypatch.setattr("async_timeline.profiler.AsyncProfiler", lambda *a: Mock(tasks=[]))

    result = runner.invoke(app, ["run", "/dev/null"])  # Invalid but mocked
    assert result.exit_code == 1
    assert "No asyncio tasks detected" in result.stdout
