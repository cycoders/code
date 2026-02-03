import pytest
import typer
from typer.testing import CliRunner
from sitemap_auditor_cli.main import app

runner = CliRunner()


def test_audit_help():
    result = runner.invoke(app, ["audit", "--help"])
    assert result.exit_code == 0
    assert "Audit sitemap" in result.stdout
    assert "--concurrency" in result.stdout


def test_version_in_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Sitemap Auditor CLI" in result.stdout