import typer
from click.testing import CliRunner
from csv_diff_cli.main import app


runner = CliRunner()


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Diff two CSV files" in result.stdout


@pytest.mark.parametrize("args,exp_code", [
    ["nonexistent1.csv", "nonexistent2.csv"],  # file not exist
    [],  # no args
])
def test_cli_errors(args, exp_code):
    result = runner.invoke(app, args)
    assert result.exit_code != 0