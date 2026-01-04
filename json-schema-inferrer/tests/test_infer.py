import json
from json_schema_inferrer.infer import infer_schema


class TestInferSchema:
    def test_single_object(self):
        sample = {
            "id": 123,
            "name": "Alice",
            "active": True,
            "scores": [95.5, 87],
        }
        schema = infer_schema([sample])
        expected = {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"},
                "active": {"const": True},
                "scores": {
                    "type": "array",
                    "items": {"type": "number", "minimum": 87, "maximum": 95.5},
                },
            },
            "required": ["id", "name", "active", "scores"],
        }
        assert schema == expected

    def test_enums(self):
        samples = [
            {"status": "active"},
            {"status": "active"},
            {"status": "inactive"},
        ]
        schema = infer_schema(samples, confidence=0.7)
        assert schema["properties"]["status"]["enum"] == ["active", "inactive"]

    def test_required_confidence(self):
        samples = [
            {"id": 1, "name": "A"},
            {"id": 2},
            {"id": 3, "name": "B"},
        ]
        schema = infer_schema(samples, confidence=0.8)
        assert "name" not in schema["required"]
        schema_low = infer_schema(samples, confidence=0.5)
        assert "name" not in schema_low["required"]

    def test_arrays_empty(self):
        sample = {"tags": []}
        schema = infer_schema([sample])
        assert schema["properties"]["tags"] == {"type": "array"}

    def test_numbers_multipleof(self):
        samples = [{"x": 10}, {"x": 20}, {"x": 30}]
        schema = infer_schema(samples)
        assert schema["properties"]["x"]["multipleOf"] == 10

    def test_nullable(self):
        samples = [{"opt": None}, {"opt": "val"}]
        schema = infer_schema(samples)
        assert schema["properties"]["opt"]["type"] == ["string", "null"]

    def test_const_bool(self):
        samples = [{"flag": True}, {"flag": True}]
        schema = infer_schema(samples)
        assert schema["properties"]["flag"]["const"] is True
