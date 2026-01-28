import pytest
from pathlib import Path
from typer.testing import CliRunner

from openapi_mocker.cli import app


runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "spec" in result.stdout

@pytest.mark.parametrize("args,expected_exit", [
    (["nonexistent.yaml"], 2),  # FileError
    (["tests/fixtures/simple.yaml"], 0),  # Would start but we don't test full
])
def test_cli_run(args: list[str], expected_exit: int, tmp_path: Path):
    # Full run exits 0 if valid, but uvicorn runs forever; test invoke only
    result = runner.invoke(app, args)
    if expected_exit == 0:
        assert result.exit_code == 0
    else:
        assert result.exit_code != 0
        assert "not found" in result.stderr
