from pathlib import Path
from typing import Union

from ariadne import load_schema_from_path, Schema


def load_schema(source: Union[Path, str]) -> Schema:
    """Load GraphQL schema from file path."""
    path = Path(source)
    if not path.exists():
        raise FileNotFoundError(f"Schema file not found: {path}")
    if not path.suffix.lower() in {'.graphql', '.gql'}:
        raise ValueError(f"Unsupported file extension: {path.suffix}. Use .graphql or .gql")
    try:
        return load_schema_from_path(path)
    except Exception as e:
        raise ValueError(f"Invalid GraphQL schema in {path}: {e}")