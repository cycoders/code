import pytest
from unittest.mock import patch
from commit_suggest_cli.suggester import get_type, get_scope, suggest_message

@pytest.fixture
def sample_changes():
    return {
        "files": ["src/ui/button.py", "src/ui/modal.py"],
        "added_lines": ["def dark_mode():"],
        "removed_lines": ["bug fix"],
    }


def test_get_type_feat(sample_changes):
    assert get_type(["add new feature"]) == "feat"


def test_get_type_fix(sample_changes):
    assert get_type(["fix bug"]) == "fix"


def test_get_type_default(sample_changes):
    assert get_type([]) == "chore"


def test_get_scope(sample_changes):
    assert get_scope(sample_changes["files"]) == "ui"


def test_get_scope_root(sample_changes):
    assert get_scope(["file.py"]) == "root"


def test_suggest_message(sample_changes):
    msg = suggest_message(sample_changes)
    assert "feat(ui):" in msg
    assert "button.py" in msg
    assert "modal.py" in msg


def test_suggest_no_files():
    msg = suggest_message({"files": [], "added_lines": [], "removed_lines": []})
    assert "chore:" in msg
