import pytest
from typer.testing import CliRunner
from cprofile_visualizer.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_cli_view_help(sample_prof: Path):
    result = runner.invoke(app, ["view", str(sample_prof), "--help"])
    assert result.exit_code == 0


@pytest.mark.parametrize("cmd", ["run", "view", "compare"])
def test_subcommands_help(cmd: str):
    result = runner.invoke(app, [cmd, "--help"])
    assert result.exit_code == 0
