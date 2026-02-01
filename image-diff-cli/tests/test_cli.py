import tempfile
from typer.testing import CliRunner

from image_diff_cli.cli import app

runner = CliRunner()


def test_diff_help():
    result = runner.invoke(app, ["diff", "--help"])
    assert result.exit_code == 0
    assert "Compare two images" in result.stdout

# Full e2e requires images, skip for brevity
# Use pytest tmp_path in integration
