from click.testing import CliRunner
from test_data_synthesizer.cli import main

def test_help():
    r = CliRunner().invoke(main, ['--help'])
    assert r.exit_code == 0