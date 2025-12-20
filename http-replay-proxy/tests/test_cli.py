import pytest
import sys
from click.testing import CliRunner
from http_replay_proxy.cli import cli

runner = CliRunner()

# typer compat via click

def test_cli_help():
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'record' in result.stdout
    assert 'replay' in result.stdout

def test_record_help():
    result = runner.invoke(cli, ['record', '--help'])
    assert result.exit_code == 0
    assert '--upstream' in result.stdout

def test_replay_missing_cassette():
    result = runner.invoke(cli, ['replay'])
    assert result.exit_code != 0
    assert '--cassette' in result.stdout