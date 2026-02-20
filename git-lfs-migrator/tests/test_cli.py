import pytest
from typer.testing import CliRunner
from git_lfs_migrator.cli import app


@pytest.fixture
 def runner():
    return CliRunner()


def test_scan_help(runner):
    result = runner.invoke(app, ["scan", "--help"])
    assert result.exit_code == 0
    assert "Scan repo history" in result.stdout


def test_migrate_no_globs(runner, mocker):
    result = runner.invoke(app, ["migrate"])
    assert result.exit_code == 2  # Bad param
    assert "Provide globs" in result.stdout

# Note: Full integration requires repo fixture, covered by unit


def test_version():
    # Via __init__
    import git_lfs_migrator
    assert git_lfs_migrator.__version__ == "0.1.0"
