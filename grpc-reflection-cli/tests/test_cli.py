from typer.testing import CliRunner

from grpc_reflection_cli.cli import app

def test_inspect_help():
    runner = CliRunner()
    result = runner.invoke(app, ["inspect", "--help"])
    assert result.exit_code == 0