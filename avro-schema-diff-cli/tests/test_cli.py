import pytest
from click.testing import CliRunner
from avro_schema_diff_cli.cli import app

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout

# More integration tests would mock files
