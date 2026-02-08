import typer
from click.testing import CliRunner
from local_service_hub.cli import app

runner = CliRunner()


def test_up_help():
    result = runner.invoke(app, ["up", "--help"])
    assert result.exit_code == 0

# CLI tests via runner
