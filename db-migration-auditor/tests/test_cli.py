import pytest
from pathlib import Path
from typer.testing import Result
from db_migration_auditor.tests.conftest import cli_runner


def test_cli_help(cli_runner):
    result: Result = cli_runner.invoke(["--help"])
    assert result.exit_code == 0
    assert "Lint SQL migrations" in result.stdout


def test_cli_lint_good(cli_runner, tmp_path: Path):
    good = tmp_path / "good.sql"
    good.write_text("SELECT 1;")
    result = cli_runner.invoke(["lint", str(good)])
    assert result.exit_code == 0
    assert "0 issues" not in result.stdout  # no output if clean


def test_cli_lint_bad(cli_runner, tmp_path: Path):
    bad = tmp_path / "bad.sql"
    bad.write_text("DROP TABLE users;")
    result = cli_runner.invoke(["lint", str(bad), "--dialect", "postgres"])
    assert result.exit_code == 1
    assert "no_drop_table" in result.stdout