from click.testing import CliRunner
from benchstat_cli.cli import cli
import tempfile, json

def test_cli_runs():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as td:
        f1 = f"{td}/a.json"
        f2 = f"{td}/b.json"
        with open(f1, 'w') as fh: json.dump({'benchmarks': [{'name': 'x', 'ns_per_op': 100}]}, fh)
        with open(f2, 'w') as fh: json.dump({'benchmarks': [{'name': 'x', 'ns_per_op': 112}]}, fh)
        result = runner.invoke(cli, [f1, f2])
        assert result.exit_code == 0