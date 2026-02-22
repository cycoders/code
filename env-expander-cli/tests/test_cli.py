import pytest
from pathlib import Path
from typer.testing import CliRunner
from env_expander_cli.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_expand(tmp_path: Path):
    sample = tmp_path / "sample.env"
    sample.write_text("A=hello\nB=${A}!")
    out = tmp_path / "out.env"
    result = runner.invoke(app, ["expand", str(sample), str(out)])
    assert result.exit_code == 0
    assert out.read_text() == "A=hello\nB=hello!\n"


def test_expand_dry_run(tmp_path: Path, capsys):
    sample = tmp_path / "sample.env"
    sample.write_text("A=1")
    runner.invoke(app, ["expand", str(sample), "/dev/null", "--dry-run"])
    captured = capsys.readouterr()
    assert "A: 1" in captured.out


def test_lint_fail(tmp_path: Path):
    sample = tmp_path / "sample.env"
    sample.write_text("A=${B}")
    result = runner.invoke(app, ["lint", str(sample)])
    assert result.exit_code == 1
    assert "Undefined" in result.stdout