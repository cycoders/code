import os
from pathlib import Path
from typer.testing import CliRunner

import pytest
from py_perf_auditor.cli import app

runner = CliRunner()


def test_scan_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Scan Python files" in result.stdout


@pytest.mark.parametrize("cmd", [["scan"], ["scan", "."]])
def test_scan_empty(cmd, tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, cmd)
    assert result.exit_code == 0
    assert "0 issues" in result.stdout


def test_scan_bad_example(tmp_path: Path):
    bad_dir = tmp_path / "examples"
    bad_dir.mkdir()
    (bad_dir / "bad.py").write_text(
        """
s = ""
for i in range(100):
    s += f"{i}"
res = list(map(len, ["a", "bb"]))
    """
    )
    result = runner.invoke(app, ["scan", str(bad_dir)])
    assert result.exit_code == 0
    assert "issues found" in result.stdout
    assert "string-concat-loop" in result.stdout
    assert "list-on-map-filter" in result.stdout


def test_scan_ignore_dir(tmp_path: Path):
    (tmp_path / "venv" / "x.py").write_text("s += 'bad'")
    result = runner.invoke(app, ["scan", str(tmp_path)])
    assert result.exit_code == 0
    assert "venv" not in result.stdout  # ignored
