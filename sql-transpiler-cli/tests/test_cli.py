import pytest
from pathlib import Path
from typer.testing import CliRunner
from sql_transpiler_cli.main import app


@pytest.fixture
 def runner():
    return CliRunner()

 def test_help(runner):
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Transpile SQL" in result.stdout

 def test_single_file_success(tmp_path, runner):
    sql_file = tmp_path / "query.sql"
    sql_file.write_text("SELECT INTERVAL '1 day';")
    result = runner.invoke(
        app, [str(sql_file), "--from", "postgres", "--to", "mysql", "--dry-run"]
    )
    assert result.exit_code == 0
    assert "Summary" in result.stdout

 def test_no_files(runner):
    result = runner.invoke(app, ["nonexistent.sql"])
    assert result.exit_code == 1
    assert "No .sql files found" in result.stdout

 def test_batch_dir(tmp_path, runner):
    dir_path = tmp_path / "sql"
    dir_path.mkdir()
    (dir_path / "a.sql").write_text("SELECT 1;")
    (dir_path / "b.sql").write_text("SELECT NOW();")
    result = runner.invoke(app, [str(dir_path), "--to", "mysql"])
    assert result.exit_code == 0
    assert "2/2" in result.stdout

 def test_output_dir(tmp_path, runner):
    input_file = tmp_path / "in.sql"
    input_file.write_text("SELECT 1;")
    out_dir = tmp_path / "out"
    result = runner.invoke(app, [str(input_file), "--output", str(out_dir)])
    assert result.exit_code == 0
    out_file = out_dir / "in.sql"
    assert out_file.exists()
    assert out_file.read_text() == "SELECT 1;"