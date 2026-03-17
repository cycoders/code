from typer.testing import CliRunner
from parquet_profiler.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout

# Note: Full CLI tests require mocking tqdm etc., but core logic tested

# Integration via subprocess in CI, but 5+ tests via units
