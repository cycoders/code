import pytest
from typer.testing import CliRunner

from openapi_auditor_cli.main import app

runner = CliRunner()


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Audit an OpenAPI specification" in result.stdout

# Note: Full CLI tests require temp files, covered by integration in other tests
