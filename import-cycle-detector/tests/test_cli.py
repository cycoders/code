import typer
from pathlib import Path
from typer.testing import CliRunner

from import_cycle_detector.cli import app

runner = CliRunner()


def test_detect_no_cycle(tmp_path: Path):
    tmp_path.joinpath("a.py").write_text("import os")
    result = runner.invoke(app, ["detect", str(tmp_path)])
    assert result.exit_code == 0
    assert "No circular" in result.stdout


def test_detect_cycle(tmp_path: Path):
    tmp_path.joinpath("a.py").write_text("from b import x")
    tmp_path.joinpath("b.py").write_text("from a import y")
    result = runner.invoke(app, ["detect", str(tmp_path)])
    assert result.exit_code == 1
    assert "cycle" in result.stdout


def test_visualize(tmp_path: Path):
    tmp_path.joinpath("a.py").touch()
    result = runner.invoke(app, ["visualize", str(tmp_path), "-o", "test.dot"])
    assert result.exit_code == 0
    assert Path("test.dot").read_text().startswith("digraph")