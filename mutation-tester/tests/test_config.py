import pytest
from pathlib import Path
from mutation_tester.config import load_config
from mutation_tester.types import Config


def test_default_config(tmp_path: Path):
    cfg = load_config(str(tmp_path), None, [], ["-q"], 30, 500, 70.0, False)
    assert isinstance(cfg, Config)
    assert cfg.target_dir == Path(tmp_path)
    assert cfg.timeout_secs == 30


def test_toml_override(tmp_path: Path):
    config_file = tmp_path / "config.toml"
    config_file.write_text("""
timeout_secs = 10
max_mutants = 100
""")
    cfg = load_config(str(tmp_path), str(config_file), [], [], 30, 500, 70.0, False)
    assert cfg.timeout_secs == 10
    assert cfg.max_mutants == 100