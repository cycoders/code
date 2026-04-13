from pathlib import Path

from pathspec import GitIgnoreSpec

from disk_usage_tui.tree_builder import build_tree

from disk_usage_tui.node import DirNode


def test_build_tree_empty(tmp_dir: Path):
    tree = build_tree(tmp_dir, GitIgnoreSpec([]))
    assert tree.size == 0
    assert tree.num_leaves == 0


def test_build_tree_files(tmp_dir: Path):
    (tmp_dir / "file1").write_bytes(b"a" * 1000)
    (tmp_dir / "file2").write_bytes(b"b" * 2000)
    tree = build_tree(tmp_dir, GitIgnoreSpec([]))
    assert tree.size == 3000
    assert tree.num_leaves == 2
    assert len(tree.children) == 2


def test_build_tree_nested(tmp_dir: Path):
    (tmp_dir / "dir1" / "file3").write_bytes(b"c" * 4000)
    tree = build_tree(tmp_dir, GitIgnoreSpec([]))
    assert tree.size == 4000
    dir1 = tree.children["dir1"]
    assert dir1.size == 4000
    assert dir1.num_leaves == 1


def test_gitignore_skip(tmp_dir: Path):
    (tmp_dir / ".gitignore").write_text("dir1/")
    (tmp_dir / "dir1" / "file").write_bytes(b"x")
    tree = build_tree(tmp_dir, load_gitignore(tmp_dir))
    assert "dir1" not in tree.children