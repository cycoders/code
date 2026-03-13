import pytest
from typer.testing import CliRunner

from monorepo_dep_aligner.cli import app

runner = CliRunner()


def test_check_no_conflict(tmp_path: Path):
    result = runner.invoke(app, ["check", str(tmp_path)])
    assert result.exit_code == 0
    assert "consistent" in result.stdout


def test_check_conflict(conflict_monorepo: Path):
    result = runner.invoke(app, ["check", str(conflict_monorepo)])
    assert result.exit_code == 1
    assert "requests" in result.stdout
    assert "conflicts" in result.stdout


def test_align_dry_run(conflict_monorepo: Path):
    result = runner.invoke(app, ["align", str(conflict_monorepo), "--dry-run"])
    assert result.exit_code == 0
    assert "align to" in result.stdout
    assert "WOULD" in result.stdout

# Note: --yes tests file changes in test_aligner