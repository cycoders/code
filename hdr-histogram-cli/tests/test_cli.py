from click.testing import CliRunner
from hdr_histogram_cli.cli import cli

def test_record_help():
    runner = CliRunner()
    result = runner.invoke(cli, ['record', '--help'])
    assert result.exit_code == 0

def test_basic_run(tmp_path):
    runner = CliRunner()
    result = runner.invoke(cli, ['record', '--input', '-', '--output', str(tmp_path/'out.hgrm')], input='42\n100\n')
    assert 'Recorded' in result.output