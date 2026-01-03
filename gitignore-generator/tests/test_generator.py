import pytest
from gitignore_generator.generator import generate_gitignore_rules


class TestGenerator:
    def test_basic_rules(self):
        langs = {"python": 5}
        fws = {"django"}
        rules = generate_gitignore_rules(langs, fws)
        assert any("__pycache__/" in r for _, r in rules)
        assert any("db.sqlite3" in r for _, r in rules)
        assert any(".DS_Store" in r for _, r in rules)
        assert len(rules) > 10

    def test_dedup(self):
        langs = {"python": 1, "javascript": 1}
        fws = set()
        rules1 = generate_gitignore_rules(langs, fws)
        rules2 = generate_gitignore_rules(langs, fws)
        assert len(rules1) == len(set(r[1] for r in rules1))  # unique rules

    def test_filter_existing(self):
        langs = {"python": 1}
        fws = set()
        existing = "__pycache__/\n"
        rules = generate_gitignore_rules(langs, fws, existing)
        assert not any("__pycache__/" in r for _, r in rules)

    def test_categories(self):
        rules = generate_gitignore_rules({}, {"react"})
        cats = {cat for cat, _ in rules}
        assert "common" in cats
        assert "fw/react" in cats