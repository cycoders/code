from pathlib import Path
from unicode_normalizer_cli.walker import walk_files, GitIgnoreMatcher


def test_gitignore_skips(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".gitignore").write_text("*.pyc")
    (repo / "skip.pyc").touch()
    (repo / "keep.py").touch()
    matcher = GitIgnoreMatcher(repo)
    files = list(walk_files(repo))
    assert len(files) == 1
    assert files[0].name == "keep.py"
    assert files[0].name != "skip.pyc"