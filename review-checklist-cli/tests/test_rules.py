import pytest
from review_checklist_cli.rules import apply_rules
from review_checklist_cli.core import ChecklistItem


def test_apply_rules_python():
    cats = {"python_source": ["foo.py", "bar.py"],
            "tests": [],
            "dependencies": ["package-lock.json"]}
    items = apply_rules(cats)
    titles = [i.title for i in items]
    assert "Run type checker" in titles
    assert "Lint Python code" in titles
    assert "Verify lockfile reproducibility" in titles


def test_apply_rules_no_python():
    cats = {"docker": ["Dockerfile"]}
    items = apply_rules(cats)
    assert any("Build Docker image" == i.title for i in items)
    assert not any("Run type checker" == i.title for i in items)