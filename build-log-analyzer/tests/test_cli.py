import pytest
from typer.testing import CliRunner
from pathlib import Path
import build_log_analyzer.cli  # noqa: F401

runner = CliRunner()


def test_help():
    result = runner.invoke(build_log_analyzer.cli.app, ["--help"])
    assert result.exit_code == 0
    assert "Analyze" in result.stdout


def test_analyze_missing(tmp_path: Path):
    result = runner.invoke(build_log_analyzer.cli.app, ["analyze", "missing.log"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_analyze_json(tmp_path: Path):
    log_file = tmp_path / "test.log"
    log_file.write_text("ERROR test")
    result = runner.invoke(build_log_analyzer.cli.app, ["analyze", str(log_file), "--json"])
    assert result.exit_code == 0
    assert '"total_errors": 1' in result.stdout


def test_compare(tmp_path: Path):
    f1 = tmp_path / "f1.log"
    f2 = tmp_path / "f2.log"
    f1.write_text("Step 1 (2s)")
    f2.write_text("Step 1 (3s)")
    result = runner.invoke(build_log_analyzer.cli.app, ["compare", str(f1), str(f2)])
    assert result.exit_code == 0  # No crash