import pytest
from typer.testing import CliRunner
from pathlib import Path

from gha_visualizer.cli import app

runner = CliRunner()


def test_render_help():
    result = runner.invoke(app, ["render", "--help"])
    assert result.exit_code == 0
    assert "Render Mermaid diagram" in result.stdout


def test_analyze_invalid_file(tmp_path: Path):
    result = runner.invoke(app, ["analyze", str(tmp_path / "missing.yml")])
    assert result.exit_code == 1
    assert "not a file" in result.stdout

# Integration test with fixture from test_parser
@pytest.mark.usefixtures("simple_workflow")
def test_cli_analyze_success(simple_workflow):
    result = runner.invoke(app, ["analyze", str(simple_workflow)])
    assert result.exit_code == 0
    assert "Number of Jobs" in result.stdout
    assert "GHA Workflow Analysis" in result.stdout