import pytest
from review_checklist_cli.core import categorize_changes, generate_checklist, ChecklistItem
from review_checklist_cli.rules import apply_rules


def test_categorize_changes():
    changes = [
        ("src/foo.py", "M"),
        ("tests/test_bar.py", "A"),
        ("Dockerfile", "M"),
        ("package-lock.json", "D"),
        ("config.yaml", "A"),
        ("README.md", "M"),
        ("secrets.txt", "A"),
    ]
    cats = categorize_changes(changes)
    assert "python_source" in cats and len(cats["python_source"]) == 1
    assert "tests" in cats
    assert "docker" in cats
    assert "dependencies" in cats
    assert "configs" in cats
    assert "docs" in cats
    assert "security" in cats


def test_generate_checklist():
    items = generate_checklist("main", "HEAD")
    assert len(items) > 5
    assert any(i.title == "Run type checker" for i in items)
    assert any(i.priority == "high" for i in items)


def test_generate_no_changes():
    # Override to empty
    pytest.skip("Covered by git_utils")
    pass