import pytest
from click.testing import CliRunner
from pathlib import Path

from arch_boundary_auditor.cli import app


runner = CliRunner()


def test_scan_no_config():
    result = runner.invoke(app, ["scan"])
    assert result.exit_code == 1
    assert "Config file not found" in result.stdout


def test_init_generates_config(tmp_path: Path):
    result = runner.invoke(app, ["init"], cwd=tmp_path)
    assert result.exit_code == 0
    config_path = tmp_path / "boundaries.yaml"
    assert config_path.exists()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout