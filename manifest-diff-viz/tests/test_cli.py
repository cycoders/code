import pytest
from typer.testing import CliRunner
from manifest_diff_viz.cli import app

runner = CliRunner()

 def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Diff two manifests" in result.stdout

 def test_cli_no_args(tmp_path):
    result = runner.invoke(app)
    assert result.exit_code == 2  # Usage error

@pytest.mark.parametrize("bad_path", ["/nonexistent", "."])
def test_missing_file(bad_path, tmp_path):
    result = runner.invoke(app, ["diff", bad_path, tmp_path / "dummy.yaml"])
    assert result.exit_code == 1
    assert "not found" in result.stdout