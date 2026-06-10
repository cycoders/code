from click.testing import CliRunner
from otel_sampling_advisor.cli import cli

def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'sampling' in result.output