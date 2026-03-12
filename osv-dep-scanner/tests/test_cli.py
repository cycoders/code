from pathlib import Path
from typer.testing import CliRunner

import pytest

from osv_dep_scanner.cli import app

runner = CliRunner()


def test_scan_invalid_path():
    result = runner.invoke(app, ["scan", "nonexistent.lock"])
    assert result.exit_code == 1
    assert "does not exist" in result.stdout


def test_scan_no_deps(tmp_path: Path, sample_package_lock: str):
    p = tmp_path / "package-lock.json"
    p.write_text('{"packages":{}}')
    with patch("osv_dep_scanner.osv_client.scan_lockfile", return_value={}):
        result = runner.invoke(app, ["scan", str(p)])
        assert result.exit_code == 0
        assert "No dependencies" in result.stdout


def test_scan_json_output(tmp_path: Path):
    p = tmp_path / "lock.json"
    p.touch()
    with patch("osv_dep_scanner.osv_client.scan_lockfile", return_value={"test": []}):
        result = runner.invoke(app, ["scan", str(p), "--output", "json"])
        assert result.exit_code == 0
        assert result.stdout.strip().startswith("{")