from typing import List

from .diff_model import DiffIssue


BREAKING_TYPES = {
    "required_added",
    "required_removed",
    "property_removed",
    "type_changed",
    "enum_removed",
    "constraint_tightened",
    "ref_changed",
}


def is_backward_compatible(issues: List[DiffIssue]) -> bool:
    """Check if new schema is backward-compatible with old (heuristic)."""

    breaking_issues = [i for i in issues if i.issue_type in BREAKING_TYPES]
    return len(breaking_issues) == 0


def get_breaking_issues(issues: List[DiffIssue]) -> List[DiffIssue]:
    """Filter breaking issues."""
    return [i for i in issues if i.issue_type in BREAKING_TYPES]