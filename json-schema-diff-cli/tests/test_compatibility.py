import pytest
from json_schema_diff_cli.compatibility import is_backward_compatible
from json_schema_diff_cli.diff_model import DiffIssue


class TestCompatibility:
    def test_no_issues_compat(self):
        assert is_backward_compatible([])

    def test_breaking_required_added(self):
        issue = DiffIssue("required_added", "/")
        assert not is_backward_compatible([issue])

    def test_breaking_type_change(self):
        issue = DiffIssue("type_changed", "/")
        assert not is_backward_compatible([issue])

    def test_non_breaking_property_added(self):
        issue = DiffIssue("property_added", "/")
        assert is_backward_compatible([issue])

    def test_mixed(self):
        breaking = DiffIssue("required_added", "/")
        non = DiffIssue("property_added", "/")
        assert not is_backward_compatible([breaking, non])