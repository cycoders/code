import pytest
from pathlib import Path
from batch_file_renamer.config import load_rules


def test_load_rules(tmp_path: Path):
    config = tmp_path / "test.yaml"
    config.write_text("rules:\n  - type: prefix\n    value: test_")
    rules = load_rules(str(config))
    assert len(rules) == 1
    assert rules[0]["type"] == "prefix"


def test_load_rules_missing(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_rules(str(tmp_path / "missing.yaml"))