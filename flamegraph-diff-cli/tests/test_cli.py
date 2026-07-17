from click.testing import CliRunner
from flamegraph_diff_cli.cli import main
import tempfile, os

def test_cli_exit_code():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmp:
        b = os.path.join(tmp, 'b.folded')
        a = os.path.join(tmp, 'a.folded')
        open(b, 'w').write('main 10\n')
        open(a, 'w').write('main 50\n')
        result = runner.invoke(main, [b, a, '--alpha', '0.1'])
        assert result.exit_code == 1