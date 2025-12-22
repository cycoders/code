import pytest
from typer.testing import CliRunner
from query_doctor_cli.__main__ import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Analyze" in result.stdout


def test_missing_files(tmp_path):
    result = runner.invoke(app, ["analyze", str(tmp_path / "nope.sql"), str(tmp_path / "nope.sql")])
    assert result.exit_code == 1
    assert "File not found" in result.stdout

# Note: Full e2e needs example files, covered in optimizer tests