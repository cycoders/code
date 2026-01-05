import json
from pathlib import Path
from typer.testing import CliRunner, Result
from schema_fixture_cli.cli import app


runner = CliRunner()


def test_cli_help() -> None:
    result: Result = runner.invoke(app, ["gen", "--help"])
    assert result.exit_code == 0
    assert "Generate schema-compliant test fixtures." in result.stdout


def test_cli_invalid_file(tmp_path: Path) -> None:
    bad_file = tmp_path / "bad.json"
    result = runner.invoke(app, ["gen", str(bad_file)])
    assert result.exit_code == 1
    assert "Error loading schema" in result.stdout


def test_cli_generate_json(tmp_path: Path) -> None:
    schema_file = tmp_path / "schema.json"
    schema_file.write_text(
        json.dumps(
            {
                "type": "object",
                "properties": {"name": {"type": "string"}},
            }
        )
    )
    result = runner.invoke(app, ["gen", str(schema_file), "--count", "1", "--seed", "42"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)
    assert len(data) == 1
    assert "name" in data[0]
