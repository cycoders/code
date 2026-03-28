from typing import List

from .models import DiffNode, ChangeType


def has_breaking_changes(diffs: List[DiffNode]) -> bool:
    """Check if any breaking changes across all nodes."""
    for diff in diffs:
        if _is_breaking_node(diff):
            return True
    return False


def _is_breaking_node(node: DiffNode) -> bool:
    # Breaking rules (subset of protobuf compatibility)
    if node.change_type == ChangeType.REMOVED and node.kind in ("field", "enum"):
        return True
    if node.kind == "field" and node.change_type == ChangeType.MODIFIED:
        # Type incompatibility (simplified)
        if node.old_value != node.new_value:
            return True
    # Recurse
    return any(_is_breaking_node(child) for child in node.children)
