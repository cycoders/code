import jsonschema
from typing import Any, List


def validate_json(instance: Any, schema: dict) -> tuple[bool, List[str]]:
    """
    Validate JSON instance against schema.

    Returns (is_valid, error_messages)
    """
    try:
        jsonschema.validate(instance=instance, schema=schema)
        return True, []
    except jsonschema.exceptions.ValidationError as exc:
        errors = []
        error = exc
        while error:
            errors.append(error.message)
            error = getattr(error, "context", None)
        return False, errors[:10]  # Limit errors
