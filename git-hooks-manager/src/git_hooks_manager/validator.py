import jsonschema

SCHEMA = {"type": "object", "properties": {"hooks": {"type": "array"}}}

def validate_config(cfg: dict) -> bool:
    jsonschema.validate(cfg, SCHEMA)
    return True