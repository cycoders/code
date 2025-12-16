import pytest
from typer.testing import CliRunner

from dupe_code_finder.main import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Detect duplicate code blocks" in result.stdout


@pytest.mark.parametrize("args, expected_rc", [(["nonexistent"], 1), (["--json"], 0)])
def test_cli_errors(args, expected_rc, tmp_path):
    result = runner.invoke(app, args + [str(tmp_path)])
    assert result.exit_code == expected_rc
