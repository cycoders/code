import json
from pathlib import Path


@pytest.fixture
def example_schema_v1() -> dict:
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number", "minimum": 0},
        },
        "required": ["name"],
    }


@pytest.fixture
def example_schema_v2_breaking() -> dict:
    return {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number", "minimum": 1},
            "email": {"type": "string"},
        },
        "required": ["name", "email"],
    }