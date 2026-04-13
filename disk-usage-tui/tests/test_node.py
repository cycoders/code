from pathlib import Path

from disk_usage_tui.node import DirNode


def test_dirnode_props():
    node = DirNode(Path("/test/file.txt"), size=1024, num_leaves=1)
    assert node.name == "file.txt"
    assert node.is_file