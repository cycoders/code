import typer
from click.testing import CliRunner

from repo_inventory_cli.main import app


runner = CliRunner()


def test_list_help():
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0

# Integration smoke tests via CLI not mocked, rely on unit


def test_config_loads():
    from repo_inventory_cli.config import load_config
    config = load_config()
    assert "paths" in config
    assert len(config["paths"]) == 4
