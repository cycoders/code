from har_to_openapi.inferrer import infer_schema_from_samples


def test_infer_object():
    samples = [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie"},
    ]
    schema = infer_schema_from_samples(samples)
    assert schema["type"] == "object"
    assert "id" in schema["properties"]
    assert schema["properties"]["id"]["type"] == "integer"
    assert "name" in schema["properties"]
    assert schema["properties"]["name"]["type"] == "string"
    assert "age" in schema["properties"]
    assert "required" == ["id", "name"]


def test_infer_array():
    samples = [[1, 2], [3, 4, 5]]
    schema = infer_schema_from_samples(samples)
    assert schema["type"] == "array"
    assert schema["items"]["type"] == "integer"


def test_infer_string_formats():
    samples = ["2024-01-01T12:00:00Z", "2024-02-01T13:00:00Z"]
    schema = infer_schema_from_samples(samples)
    assert "format" in schema
    assert schema["format"] == "date-time"


def test_empty_samples():
    assert infer_schema_from_samples([])["type"] == "null"
