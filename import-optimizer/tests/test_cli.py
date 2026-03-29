import typer
test_runner = typer.testing.CliRunner()


def test_scan_help(test_runner):
    result = test_runner.invoke(["scan", "--help"])
    assert result.exit_code == 0
    assert "Scan files/directories" in result.stdout


def test_optimize_help(test_runner):
    result = test_runner.invoke(["optimize", "--help"])
    assert result.exit_code == 0
    assert "Optimize imports" in result.stdout