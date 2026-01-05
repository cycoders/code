import pytest
from faker import Faker
import random

from schema_fixture_cli.generator import generate_fixture, inline_schema


@pytest.fixture
def faker():
    return Faker(seed=42)


class TestGenerateFixture:
    def test_string(self, faker):
        schema = {"type": "string"}
        val = generate_fixture(schema, faker)
        assert isinstance(val, str)
        assert len(val) > 0

    def test_email_format(self, faker):
        schema = {"type": "string", "format": "email"}
        val = generate_fixture(schema, faker)
        assert "@" in val

    def test_integer_range(self, faker):
        schema = {"type": "integer", "minimum": 10, "maximum": 20}
        val = generate_fixture(schema, faker)
        assert 10 <= val <= 20
        assert isinstance(val, int)

    def test_boolean(self, faker):
        schema = {"type": "boolean"}
        val = generate_fixture(schema, faker)
        assert isinstance(val, bool)

    def test_enum(self, faker):
        schema = {"type": "string", "enum": ["foo", "bar", "baz"]}
        val = generate_fixture(schema, faker)
        assert val in ["foo", "bar", "baz"]

    def test_array(self, faker):
        schema = {"type": "array", "items": {"type": "string"}}
        val = generate_fixture(schema, faker)
        assert isinstance(val, list)
        assert len(val) > 0
        assert all(isinstance(i, str) for i in val)

    def test_object(self, faker):
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        }
        val = generate_fixture(schema, faker)
        assert isinstance(val, dict)
        assert "name" in val
        assert isinstance(val["name"], str)

    def test_object_optional(self, faker):
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
            },
            "required": ["name"],
        }
        val = generate_fixture(schema, faker)
        assert "name" in val
        # age may or may not be there

    def test_oneof(self, faker):
        schema = {
            "oneOf": [
                {"type": "string"},
                {"type": "integer"},
            ]
        }
        val = generate_fixture(schema, faker)
        assert isinstance(val, (str, int))

    def test_pattern(self, faker):
        schema = {"type": "string", "pattern": "[a-z]{3}-[0-9]{3}"}
        val = generate_fixture(schema, faker)
        assert "-" in val and len(val) == 7


class TestInlineSchema:
    def test_no_ref(self):
        schema = {"type": "string"}
        resolver = None  # type: ignore
        assert inline_schema(schema, resolver) == schema  # Simplified test

    # More resolver tests in integration
