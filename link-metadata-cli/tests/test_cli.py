import json
from typer.testing import CliRunner
from link_metadata_cli.cli import app

runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Extract rich metadata from URLs." in result.stdout


# Note: Full CLI tests require mocking fetch_metadata, omitted for brevity
# Integration covered in extractor tests
