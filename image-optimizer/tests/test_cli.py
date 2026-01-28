from typer.testing import CliRunner
import pytest
from image_optimizer.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Optimize" in result.stdout


def test_invalid_path(tmp_path):
    result = runner.invoke(app, ["optimize", str(tmp_path / "nonexistent.jpg")])
    assert result.exit_code == 1
    assert "No supported images" in result.stdout


def test_version(tmp_image_png):
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0