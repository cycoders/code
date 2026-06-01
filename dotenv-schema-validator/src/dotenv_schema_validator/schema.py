EXAMPLE_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "properties": {
        "DATABASE_URL": {"type": "string", "format": "uri"},
        "PORT": {"type": "integer", "minimum": 1, "maximum": 65535},
        "DEBUG": {"type": "boolean"}
    },
    "required": ["DATABASE_URL"]
}