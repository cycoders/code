import json
from serdes_bench.generator import generate_sample_data


def test_generate_simple():
    data = generate_sample_data("simple", 100)
    assert isinstance(data, dict)
    assert "id" in data
    assert isinstance(data["tags"], list)


def test_generate_nested():
    data = generate_sample_data("nested", 500)
    assert isinstance(data, dict)
    assert "root" in data
    assert isinstance(data["root"], list)


def test_generate_array():
    data = generate_sample_data("array-heavy", 100)
    assert len(data["batch"]) == 100


def test_json_serializable():
    for kind in ["simple", "nested", "array-heavy"]:
        data = generate_sample_data(kind)
        json.dumps(data)  # No error
