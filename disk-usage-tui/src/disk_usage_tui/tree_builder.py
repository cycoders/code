import os
import sys
from pathlib import Path
from typing import Optional

from pathspec import GitIgnoreSpec

from .node import DirNode


def build_tree(root: Path, gitignore: GitIgnoreSpec) -> DirNode:
    """Build DirNode tree with sizes, gitignore-aware."""
    sys.setrecursionlimit(10000)

    root_node = DirNode(root)

    def _scan(current: Path, node: DirNode) -> None:
        size = 0
        try:
            entries = list(current.iterdir())
        except (PermissionError, OSError):
            node.size = 0
            node.num_leaves = 0
            return

        for entry in sorted(entries, key=lambda e: e.name):
            rel = str(entry.relative_to(root))
            if gitignore.match_file(rel):
                continue

            try:
                st = entry.stat(follow_symlinks=False)
            except OSError:
                continue

            if entry.is_dir(follow_symlinks=False):
                child = DirNode(entry)
                _scan(entry, child)
                if child.size > 0:
                    size += child.size
                    node.children[entry.name] = child
            else:
                fsize = st.st_size
                size += fsize
                child = DirNode(entry, fsize)
                node.children[entry.name] = child

        node.size = size
        node.num_leaves = 1 if not node.children else sum(c.num_leaves for c in node.children.values())

    _scan(root, root_node)
    return root_node