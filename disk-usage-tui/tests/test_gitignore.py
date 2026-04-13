from pathlib import Path
from pathspec import GitIgnoreSpec

from disk_usage_tui.gitignore import load_gitignore


def test_load_gitignore(tmp_dir: Path):
    (tmp_dir / ".gitignore").write_text("node_modules/\n**/*.log")
    spec = load_gitignore(tmp_dir)
    assert isinstance(spec, GitIgnoreSpec)
    assert spec.match_file("node_modules")