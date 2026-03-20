from pathlib import Path
import json
from typing import List, Dict, Any


def load_schema(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e
    except Exception as e:
        raise ValueError(f"Cannot read {path}: {e}") from e


def get_schemas(directory: Path) -> List[Dict[str, Any]]:
    schemas = []
    for p in directory.glob("*.avsc"):
        schemas.append(load_schema(p))
    return schemas


def validate_schema(schema: Dict[str, Any]) -> None:
    if "type" not in schema:
        raise ValueError("Schema missing 'type' field")
    # Additional validation could use avro-python3 but kept dep-free
