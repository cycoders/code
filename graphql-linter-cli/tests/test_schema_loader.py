import pytest
from pathlib import Path
from graphql_linter_cli.schema_loader import load_schema


def test_load_valid_schema(examples_dir: Path):
    schema = load_schema(examples_dir / "good.graphql")
    assert schema


def test_load_invalid_file(examples_dir: Path):
    with pytest.raises(FileNotFoundError):
        load_schema(examples_dir / "missing.graphql")


def test_load_non_graphql(examples_dir: Path):
    with pytest.raises(ValueError, match="Unsupported file extension"):
        load_schema(examples_dir / "test.txt")


def test_load_invalid_syntax(examples_dir: Path):
    path = examples_dir / "bad.graphql"
    with pytest.raises(ValueError, match="Invalid GraphQL schema"):
        load_schema(path)