from pathlib import Path
import typer
from typer.testing import CliRunner

from i18n_extractor.main import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Extract translatable strings" in result.stdout


def test_no_args(tmp_path):
    result = runner.invoke(app)
    assert result.exit_code != 0  # expects paths
