from typing import Any, Dict, TypedDict

from jsonschema import Draft7Validator

PWA_MANIFEST_SCHEMA: Dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/07/schema#",
    "type": "object",
    "required": ["name", "short_name", "start_url", "display", "icons"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "short_name": {"type": "string", "minLength": 1},
        "start_url": {"type": "string"},
        "scope": {"type": "string"},
        "display": {
            "type": "string",
            "enum": ["browser", "minimal-ui", "standalone", "fullscreen"],
        },
        "start_url": {"type": "string"},
        "icons": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["src", "sizes"],
                "properties": {
                    "src": {"type": "string", "format": "uri"},
                    "sizes": {"type": "string", "pattern": "\\d+x\\d+(?: (?:\\d+x\\d+))*"},
                    "type": {"type": "string"},
                    "purpose": {"type": "string"},
                },
            },
        },
        "theme_color": {"type": "string"},
        "background_color": {"type": "string"},
        "categories": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": True,
}

MANIFEST_VALIDATOR = Draft7Validator(PWA_MANIFEST_SCHEMA)
