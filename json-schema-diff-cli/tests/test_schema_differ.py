import pytest
from json_schema_diff_cli.schema_differ import diff_schemas
from json_schema_diff_cli.diff_model import DiffIssue


class TestSchemaDiffer:
    def test_no_changes(self, example_schema_v1):
        issues = diff_schemas(example_schema_v1, example_schema_v1)
        assert len(issues) == 0

    def test_type_change(self, example_schema_v1):
        s2 = example_schema_v1.copy()
        s2["type"] = "array"
        issues = diff_schemas(example_schema_v1, s2)
        assert any(i.issue_type == "type_changed" for i in issues)

    def test_required_added(self, example_schema_v1):
        s2 = example_schema_v1.copy()
        s2["required"].append("age")
        issues = diff_schemas(example_schema_v1, s2)
        assert any(i.issue_type == "required_added" for i in issues)

    def test_property_added(self, example_schema_v1):
        s2 = example_schema_v1.copy()
        s2["properties"]["email"] = {"type": "string"}
        issues = diff_schemas(example_schema_v1, s2)
        assert any(i.issue_type == "property_added" for i in issues)

    def test_property_removed(self, example_schema_v1):
        s2 = example_schema_v1.copy()
        del s2["properties"]["name"]
        issues = diff_schemas(example_schema_v1, s2)
        assert any(i.issue_type == "property_removed" for i in issues)

    def test_enum_removed(self):
        s1 = {"type": "string", "enum": ["a", "b"]}
        s2 = {"type": "string", "enum": ["a"]}
        issues = diff_schemas(s1, s2)
        assert any(i.issue_type == "enum_removed" for i in issues)

    def test_constraint_tightened(self, example_schema_v1):
        s2 = example_schema_v1.copy()
        s2["properties"]["age"]["minimum"] = 18
        issues = diff_schemas(example_schema_v1, s2)
        assert any(i.issue_type == "constraint_tightened" for i in issues)

    def test_array_items(self):
        s1 = {"type": "array", "items": {"type": "string"}}
        s2 = {"type": "array", "items": {"type": "number"}}
        issues = diff_schemas(s1, s2)
        assert len(issues) > 0