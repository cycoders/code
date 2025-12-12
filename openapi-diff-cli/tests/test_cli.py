import json
import tempfile
from pathlib import Path
from typing import Dict, Any

import pytest
import typer
from typer.testing import CliRunner

import yaml

from src.openapi_diff_cli.cli import app

runner = CliRunner()


@pytest.fixture
def simple_specs(tmp_path: Path) -> tuple[Path, Path]:
    old_file = tmp_path / "old.yaml"
    new_file = tmp_path / "new.yaml"
    old_data = {
        "openapi": "3.0.0",
        "paths": {
            "/old": {"get": {"parameters": [], "responses": {"200": {"description": "ok"}}}}
        },
    }
    new_data = {
        "openapi": "3.0.0",
        "paths": {
            "/old": {
                "get": {
                    "parameters": [
                        {"name": "q", "in": "query", "schema": {"type": "string"}}
                    ],
                    "responses": {},
                }
            },
            "/new": {"get": {}},
        },
    }
    old_file.write_text(yaml.dump(old_data))
    new_file.write_text(yaml.dump(new_data))
    return old_file, new_file


def test_cli_diff_table(simple_specs: tuple[Path, Path]) -> None:
    old, new = simple_specs
    result = runner.invoke(app, [str(old), str(new)])
    assert result.exit_code == 0
    assert "Summary" in result.stdout
    assert "breaking" in result.stdout
    assert "non-breaking" in result.stdout


def test_cli_fail_fast(simple_specs: tuple[Path, Path]) -> None:
    old, new = simple_specs
    result = runner.invoke(app, [str(old), str(new), "--fail-on-breaking"])
    assert result.exit_code == 1
    assert "breaking changes detected" in result.stderr


def test_cli_json_output(tmp_path: Path, simple_specs: tuple[Path, Path]) -> None:
    old, _ = simple_specs
    json_file = tmp_path / "out.json"
    result = runner.invoke(app, [str(old), str(old), "--json", str(json_file)])
    assert result.exit_code == 0
    data = json.loads(json_file.read_text())
    assert data["summary"]["total_changes"] == 0
