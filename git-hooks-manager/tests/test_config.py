from pathlib import Path
from git_hooks_manager.config import load_config

def test_load_empty(tmp_path):
    p = tmp_path / "empty.yaml"
    p.write_text("")
    assert load_config(p) == {}