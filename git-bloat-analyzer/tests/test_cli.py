import json
from pathlib import Path
from typer.testing import CliRunner

from git_bloat_analyzer.cli import app

runner = CliRunner()


def test_analyze_valid(mini_repo: Path, capsys):
    result = runner.invoke(app, ["analyze", str(mini_repo)])
    assert result.exit_code == 0
    captured = capsys.readouterr()
    assert "large.bin" in captured.out
    assert "MiB" in captured.out


def test_not_git_repo(tmp_path: Path):
    result = runner.invoke(app, ["analyze", str(tmp_path)])
    assert result.exit_code == 1
    assert "Not a Git repository." in result.stdout