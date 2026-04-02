import pytest
import yaml
from pathlib import Path
from typer.testing import CliRunner

from backfill_planner.cli import app


@pytest.mark.parametrize("invoke_args,exit_code", [
    (["plan", "nonexistent.yaml"], 1),
])
def test_cli_errors(runner, tmp_path, sample_config_dict, invoke_args, exit_code):
    config_path = tmp_path / "config.yaml"
    yaml.dump(sample_config_dict, config_path.open("w"))

    if invoke_args[1] == "nonexistent.yaml":
        result = runner.invoke(app, invoke_args)
    else:
        result = runner.invoke(app, ["plan", str(config_path)])

    assert result.exit_code == exit_code
    if exit_code == 0:
        assert "Backfill Plan" in result.stdout


# Note: Full CLI test relies on yaml fixture; simplified for core logic
