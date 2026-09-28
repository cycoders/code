from typer.testing import CliRunner
from ast_query_cli.cli import app

def test_help():
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0

def test_basic_run(tmp_path):
    f = tmp_path / "a.py"
    f.write_text("db.execute()\n")
    runner = CliRunner()
    result = runner.invoke(app, ["--pattern", "Call", str(tmp_path)])
    assert result.exit_code == 0