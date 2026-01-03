import pytest
from typer.testing import CliRunner
from gitignore_generator.cli import app
from pathlib import Path

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Generate tailored .gitignore" in result.stdout


@pytest.mark.parametrize("args,expected", [
    (["."], 0),
    (["nonexistent"], 1),
])
def test_cli_errors(tmp_path, args, expected):
    result = runner.invoke(app, ["generate", str(tmp_path)] + args)
    assert result.exit_code == expected