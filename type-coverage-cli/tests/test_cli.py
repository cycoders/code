import sys
from pathlib import Path

from typer.testing import CliRunner

from type_coverage_cli.cli import app

runner = CliRunner()


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_no_args(tmp_path: Path):
    (tmp_path / "empty").mkdir()
    result = runner.invoke(app, [str(tmp_path)])
    assert result.exit_code == 0
    assert "No Python functions found" in result.stdout


def test_fail_below(sample_py_file):
    code = "def foo(): pass"  # 0% coverage
    sample_py_file.write_text(code)
    result = runner.invoke(app, [str(sample_py_file.parent), "--fail-below", "1"])
    assert result.exit_code == 1