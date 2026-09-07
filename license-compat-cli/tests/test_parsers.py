from pathlib import Path
from license_compat_cli.parsers import detect_lockfile

def test_detect_poetry(tmp_path):
    (tmp_path / "poetry.lock").touch()
    assert detect_lockfile(tmp_path).name == "poetry.lock"