import pytest

from proto_schema_diff.models import ChangeType, DiffNode
from proto_schema_diff.rules import has_breaking_changes, _is_breaking_node


def test_removed_field_breaking():
    node = DiffNode(
        path="user.name", kind="field", change_type=ChangeType.REMOVED
    )
    assert _is_breaking_node(node)


def test_type_change_breaking():
    node = DiffNode(
        path="user.id",
        kind="field",
        change_type=ChangeType.MODIFIED,
        old_value=(5, ""),
        new_value=(1, ""),
    )
    assert _is_breaking_node(node)


def test_added_not_breaking():
    node = DiffNode(path="user.new", kind="field", change_type=ChangeType.ADDED)
    assert not _is_breaking_node(node)


def test_has_breaking():
    breaking_node = DiffNode(path="bad", kind="field", change_type=ChangeType.REMOVED)
    diffs = [DiffNode(path="good", kind="file", children=[breaking_node])]
    assert has_breaking_changes(diffs)
