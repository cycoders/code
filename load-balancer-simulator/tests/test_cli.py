import typer
from click.testing import CliRunner
from load_balancer_simulator.cli import app


runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Run load balancer simulation" in result.stdout


def test_cli_invalid(mocker):
    mocker.patch("load_balancer_simulator.cli.Config.model_validate", side_effect=ValueError("boom"))
    result = runner.invoke(app, ["sim", "--arrival-rate", "-1"])
    assert result.exit_code == 1