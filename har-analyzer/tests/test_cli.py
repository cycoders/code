import json
from pathlib import Path
from typer.testing import CliRunner
from har_analyzer.cli import app

runner = CliRunner()


def test_analyze_valid(tmp_path: Path, sample_har_path):
    result = runner.invoke(app, ["analyze", str(sample_har_path)])
    assert result.exit_code == 0
    assert "HAR Analyzer" in result.stdout


def test_analyze_invalid_json(tmp_path: Path):
    bad_file = tmp_path / "bad.har"
    bad_file.write_text("invalid json")
    result = runner.invoke(app, ["analyze", str(bad_file)])
    assert result.exit_code == 1
    assert "Invalid JSON" in result.stdout


def test_analyze_no_log(tmp_path: Path):
    no_log = tmp_path / "nolog.har"
    no_log.write_text(json.dumps({"foo": "bar"}))
    result = runner.invoke(app, ["analyze", str(no_log)])
    assert result.exit_code == 1
    assert "Invalid HAR" in result.stdout


def test_analyze_no_entries(tmp_path: Path):
    no_entries = tmp_path / "noentries.har"
    no_entries.write_text(json.dumps({"log": {"version": "1.2"}}))
    result = runner.invoke(app, ["analyze", str(no_entries)])
    assert result.exit_code == 0
    assert "No entries" in result.stdout


def test_file_not_found(tmp_path: Path):
    result = runner.invoke(app, ["analyze", "nonexistent.har"])
    assert result.exit_code == 1
    assert "File not found" in result.stdout