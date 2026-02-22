import yaml
import re
from typing import Dict, List, Any


def load_schema(schema_file: Path) -> Dict[str, Any]:
    """Load YAML schema."""
    with schema_file.open() as f:
        return yaml.safe_load(f) or {}


def validate_env(env: Dict[str, str], schema: Dict[str, Any]) -> List[str]:
    """Validate expanded env against schema."""
    errors = []

    # Required
    required = schema.get('required', [])
    for var in required:
        if var not in env:
            errors.append(f"Missing required variable: {var}")

    # Patterns
    patterns = schema.get('patterns', {})
    for var, pat in patterns.items():
        if var in env and not re.match(pat, env[var]):
            errors.append(f"'{var}' does not match pattern '{pat}': {env[var]!r}")

    # Types
    types_ = schema.get('types', {})
    for var, typ in types_.items():
        if var in env:
            value = env[var]
            try:
                if typ == 'int':
                    int(value)
                elif typ == 'float':
                    float(value)
                elif typ == 'bool':
                    if value.lower() not in ('true', 'false', '1', '0', 'yes', 'no', 'on', 'off'):
                        raise ValueError
            except ValueError:
                errors.append(f"'{var}' is not a valid {typ}: {value!r}")

    return errors