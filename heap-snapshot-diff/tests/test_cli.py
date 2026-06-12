from typer.testing import CliRunner
from heap_snapshot_diff.cli import app

def test_help():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0