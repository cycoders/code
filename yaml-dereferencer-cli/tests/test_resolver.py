import pytest
from pathlib import Path
from ruamel.yaml import YAML

from yaml_dereferencer_cli.resolver import (
    validate_yaml,
    resolve_yaml,
    get_sharing_stats,
    ResolutionError,
    DuplicateAnchorError,
    CycleError,
)

yaml = YAML(typ="rt")

SIMPLE = """
a: &x
  b: 1
  c: 2

d: *x
e: &y {f: *x}
"""

NESTED = """
shared: &list
  - &item 42
  - *item
merge:
  <<: *list
  extra: foo
"""

DUPLICATE = """
a: &x 1
b: &x 2
"""

@pytest.fixture
def simple_data():
    return yaml.load(SIMPLE)

class TestResolve:
    def test_simple_resolve(self, simple_data):
        data = validate_yaml(SIMPLE)
        assert data is simple_data
        derefed = resolve_yaml(data)
        assert "&x" not in derefed
        assert "*x" not in derefed
        assert derefed.count("b: 1") == 2  # Duplicated

    def test_nested_resolve(self):
        data = validate_yaml(NESTED)
        derefed = resolve_yaml(data)
        assert derefed.count("42") == 3  # list[0], list[1], merge

    def test_merge_resolve(self):
        data = validate_yaml(NESTED)
        derefed = resolve_yaml(data)
        assert "extra: foo" in derefed

class TestValidate:
    def test_valid(self):
        validate_yaml(SIMPLE)
        validate_yaml(NESTED)

    def test_invalid_yaml(self):
        with pytest.raises(ResolutionError):
            validate_yaml("invalid: yaml")

    def test_duplicate_anchor(self):
        with pytest.raises(DuplicateAnchorError):
            validate_yaml(DUPLICATE)

    def test_cycle(self):
        cycle_yaml = """
a: &x
  b: &y []
  c: *y
"""
        with pytest.raises(CycleError):
            validate_yaml(cycle_yaml)

class TestStats:
    def test_sharing_stats(self):
        stats = get_sharing_stats(SIMPLE)
        assert stats["shared_anchors"] == {"x": 2}
        assert stats["total_anchors"] == 2
        assert "shared_nodes" in stats

    def test_no_sharing(self):
        no_share = "a: 1\nb: 2"
        stats = get_sharing_stats(no_share)
        assert stats["shared_anchors"] == {}
