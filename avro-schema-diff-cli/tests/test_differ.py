import pytest
from avro_schema_diff_cli.differ import check_type_compatible, get_schema_diff


@pytest.fixture
def simple_old():
    return {"type": "record", "name": "Test", "fields": [{"name": "f", "type": "int"}]}

@pytest.fixture
def simple_new():
    return {"type": "record", "name": "Test", "fields": [{"name": "f", "type": "long"}]}


def test_primitive_promotion():
    assert check_type_compatible("int", "long")
    assert check_type_compatible("int", "double")
    assert not check_type_compatible("long", "int")


def test_record_field_promotion(simple_old, simple_new):
    assert check_type_compatible(simple_old, simple_new)


def test_record_missing_field():
    old = {"type": "record", "fields": [{"name": "f", "type": "int"}]}
    new = {"type": "record", "fields": []}
    assert not check_type_compatible(old, new)


def test_enum_subset():
    old_enum = {"type": "enum", "symbols": ["A", "B"]}
    new_enum = {"type": "enum", "symbols": ["A", "B", "C"]}
    assert check_type_compatible(old_enum, new_enum)
    assert not check_type_compatible(new_enum, old_enum)


def test_union_resolution():
    assert check_type_compatible(["int", "null"], ["long", "null"])
    assert not check_type_compatible(["string"], ["int"])


def test_array_map():
    arr_old = {"type": "array", "items": "int"}
    arr_new = {"type": "array", "items": "long"}
    assert check_type_compatible(arr_old, arr_new)


def test_schema_diff_added_removed(simple_old, simple_new):
    new_added = simple_new.copy()
    new_added["fields"].append({"name": "g", "type": "string"})
    diff = get_schema_diff(simple_old, new_added)
    assert "g" in diff["added"]
    assert diff["backward_compatible"]

    new_removed = simple_old.copy()
    new_removed["fields"] = []
    diff = get_schema_diff(simple_old, new_removed)
    assert "f" in diff["removed"]
    assert not diff["backward_compatible"]
