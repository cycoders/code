import random
from typing import Any, Dict, List, Union, Callable
from faker import Faker
from jsonschema import RefResolver


def inline_schema(schema: Any, resolver: RefResolver) -> Any:
    """Recursively inline $ref schemas."""
    if isinstance(schema, dict) and "$ref" in schema:
        ref = schema["$ref"]
        _, resolved = resolver.resolve(ref)
        return inline_schema(resolved, resolver)
    elif isinstance(schema, dict):
        return {k: inline_schema(v, resolver) for k, v in schema.items()}
    elif isinstance(schema, list):
        return [inline_schema(item, resolver) for item in schema]
    return schema


def generate_fixture(schema: Dict[str, Any], faker: Faker) -> Any:
    """Generate a single fixture instance from inlined schema."""

    # Enum or const
    if "enum" in schema:
        return random.choice(schema["enum"])
    if "const" in schema:
        return schema["const"]

    typ = schema.get("type")
    if isinstance(typ, list):
        sub_typ = random.choice(typ)
        return generate_fixture({"type": sub_typ, **{k: v for k, v in schema.items() if k != "type"}}, faker)

    if typ == "null":
        return None
    if typ == "boolean":
        return faker.boolean(chance_of_getting_true=50)
    if typ == "integer":
        return _generate_number(schema, faker, int)
    if typ == "number":
        return _generate_number(schema, faker, float)
    if typ == "string":
        return _generate_string(schema, faker)
    if typ == "array":
        return _generate_array(schema, faker)
    if typ == "object":
        return _generate_object(schema, faker)

    # oneOf/anyOf: random subschema
    subschemas = schema.get("oneOf") or schema.get("anyOf")
    if subschemas:
        sub_schema = random.choice(subschemas)
        return generate_fixture(sub_schema, faker)

    # Fallback
    c.print(f"[yellow]Unknown type '{typ}', defaulting to string[/yellow]")
    return faker.word()


def _generate_number(schema: Dict, faker: Faker, num_type: Callable) -> Union[int, float]:
    min_val = schema.get("minimum", schema.get("exclusiveMinimum", -10000))
    max_val = schema.get("maximum", schema.get("exclusiveMaximum", 10000))
    if "exclusiveMinimum" in schema:
        min_val += 1 if num_type is int else 1e-6
    if "exclusiveMaximum" in schema:
        max_val -= 1 if num_type is int else 1e-6
    if num_type is int:
        return faker.random_int(min_val, max_val)
    return faker.pyfloat(min_value=min_val, max_value=max_val, positive=False)


def _generate_string(schema: Dict, faker: Faker) -> str:
    if "pattern" in schema:
        return faker.regexify(schema["pattern"])

    fmt = schema.get("format")
    format_map: Dict[str, Callable[[], str]] = {
        "date": lambda: faker.date_this_decade(),
        "date-time": lambda: faker.date_time_this_year().isoformat(),
        "time": faker.time,
        "email": faker.email,
        "hostname": faker.hostname,
        "ipv4": faker.ipv4,
        "ipv6": faker.ipv6,
        "uri": faker.uri,
        "uuid": lambda: str(faker.uuid4()),
    }
    if fmt in format_map:
        return format_map[fmt]()

    # Default string
    min_len = schema.get("minLength", 1)
    max_len = schema.get("maxLength", 50)
    return faker.text(max_nb_chars=max_len)[:max_len].strip() or faker.word()


def _generate_array(schema: Dict, faker: Faker) -> List[Any]:
    items_schema = schema.get("items", {})
    min_items = schema.get("minItems", 0)
    max_items = schema.get("maxItems", max(min_items + 5, 10))
    num_items = faker.random_int(min_items, max_items)
    return [generate_fixture(items_schema, faker) for _ in range(num_items)]


def _generate_object(schema: Dict, faker: Faker) -> Dict[str, Any]:
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    result: Dict[str, Any] = {}

    # Required first
    for prop_name in required:
        if prop_name in properties:
            result[prop_name] = generate_fixture(properties[prop_name], faker)

    # Optional ~70% chance
    for prop_name, prop_schema in properties.items():
        if prop_name not in required and random.random() < 0.7:
            result[prop_name] = generate_fixture(prop_schema, faker)

    return result
