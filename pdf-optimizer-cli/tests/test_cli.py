import pathlib
import pytest
from typer.testing import CliRunner

from pdf_optimizer_cli.cli import app

runner = CliRunner()


def test_help_command(monkeypatch):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_optimize_no_args(monkeypatch):
    result = runner.invoke(app, ["optimize"])
    assert result.exit_code == 2  # Missing arg
    assert "Missing argument 'INPUT_PATH'" in result.stdout


def test_optimize_invalid_file(tmp_path, monkeypatch):
    fake_pdf = tmp_path / "fake.txt"
    fake_pdf.write_text("not pdf")
    result = runner.invoke(app, ["optimize", str(fake_pdf)])
    # Would fail on pikepdf open, but CLI catches
    assert result.exit_code != 0


# Note: Full PDF tests skipped without sample PDF; image tests cover core logic


@pytest.mark.skip(reason="Requires sample PDF; covered by integration")
def test_full_optimize(tmp_path):
    pass
