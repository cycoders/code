import logging
import random
from typing import Any, Dict, List

from faker import Faker

fake = Faker()
logger = logging.getLogger(__name__)


def generate_mock(schema: Dict[str, Any], depth: int = 5) -> Any:
    """
    Recursively generate fake data matching the JSON schema.

    Supports: primitives, objects, arrays, nesting, formats, enums.
    Depth-limited to prevent infinite recursion.

    Args:
        schema: JSON schema dict.
        depth: Recursion limit.

    Returns:
        Fake data instance.
    """
    if depth <= 0:
        logger.warning("Max depth reached, returning None")
        return None

    typ = schema.get('type', 'null')

    if typ == 'null' or typ == 'any':
        return None

    elif typ == 'string':
        format_ = schema.get('format')
        if format_ == 'email':
            return fake.email()
        elif format_ == 'uuid':
            return str(fake.uuid4())
        elif format_ == 'date':
            return fake.date_iso_format()
        elif format_ == 'date-time':
            return fake.iso8601()
        elif 'enum' in schema:
            return random.choice(schema['enum'])
        else:
            return fake.word()

    elif typ == 'number':
        return round(fake.pyfloat(left_digits=3, right_digits=2), 2)
    elif typ == 'integer':
        return fake.random_int(min=0, max=10000)

    elif typ == 'boolean':
        return fake.boolean(chance_of_getting_true=50)

    elif typ == 'object':
        properties = schema.get('properties', {})
        required = set(schema.get('required', []))
        result: Dict[str, Any] = {}
        for prop, subschema in properties.items():
            if prop in required or random.random() > 0.3:  # 70% chance optional
                result[prop] = generate_mock(subschema, depth - 1)
        return result

    elif typ == 'array':
        items_schema = schema.get('items', {})
        min_items = schema.get('minItems', 0)
        max_items = schema.get('maxItems', 10)
        num_items = max(min_items, random.randint(1, max_items or 5))
        return [generate_mock(items_schema, depth - 1) for _ in range(num_items)]

    logger.warning(f"Unsupported type '{typ}', defaulting to str")
    return fake.word()