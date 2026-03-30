import sys
from click.testing import CliRunner
from aio_task_monitor.cli import app

runner = CliRunner()


def test_monitor_help():
    result = runner.invoke(app, ["monitor", "--help"])
    assert result.exit_code == 0


def test_snapshot_table(monkeypatch, capsys):
    monkeypatch.setattr("aio_task_monitor.snapshot.take_snapshot", lambda: {
        "stats": {"num_tasks": 1},
        "tasks": [{"task_id": 123, "name": "test", "coro_name": "test", "done": False, "cancelled": False, "stack": []}],
    })
    result = runner.invoke(app, ["snapshot"])
    assert result.exit_code == 0
    captured = capsys.readouterr()
    assert "ID" in captured.out


def test_snapshot_json(monkeypatch, capsys):
    monkeypatch.setattr("aio_task_monitor.snapshot.take_snapshot", lambda: {"stats": {}, "tasks": []})
    result = runner.invoke(app, ["snapshot", "--json"])
    assert result.exit_code == 0
    captured = capsys.readouterr()
    assert '{"stats":' in captured.out
