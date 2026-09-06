from pathlib import Path
from git_hooks_manager.installer import install_hook

def test_install_dry_run(tmp_path):
    install_hook("pre-commit", "#!/bin/sh\necho hi", tmp_path, dry_run=True)
    assert not (tmp_path / "hooks" / "pre-commit").exists()