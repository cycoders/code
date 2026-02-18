import pathlib
from typer.testing import Result

from sql_index_suggester.tests.conftest import runner


def test_cli_help():
    result: Result = runner.invoke(sql_index_suggester.cli.app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_cli_errors(tmp_path: pathlib.Path, sample_schema, sample_queries):
    schema_path = tmp_path / "schema.sql"
    schema_path.write_text(sample_schema)
    result = runner.invoke(sql_index_suggester.cli.app, [str(schema_path), "missing.sql"])
    assert result.exit_code == 1
