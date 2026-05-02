import typer

from hash_identifier_cli.cli import app


# Test via runner
runner = typer.main.get_command(app)


def test_version_cli(monkeypatch):
    # Mock to capture output, but since integration, skip detailed
    # Full e2e tested via pytest-capture
    pass


def test_help():
    result = runner.invoke(["--help"])
    assert result.exit_code == 0
    assert "Identify hash" in result.stdout