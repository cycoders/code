from click.testing import CliRunner
from metrics_cardinality_cli.cli import main

def test_help():
    r = CliRunner().invoke(main, ["--help"])
    assert r.exit_code == 0

def test_analyze_table_output():
    data = "m{l=\"x\"} 1\n"
    r = CliRunner().invoke(main, ["analyze", "--threshold", "1", "-"], input=data)
    assert "m" in r.output