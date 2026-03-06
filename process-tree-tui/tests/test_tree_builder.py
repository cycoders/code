import psutil
from unittest.mock import Mock, patch
from collections import defaultdict

from process_tree_tui.tree_builder import populate_tree, _populate_children
from textual.widgets import Tree


@patch("psutil.process_iter")
def test_populate_tree_empty(mock_iter, mock_process):
    mock_iter.return_value = []
    tree = Tree("test")
    populate_tree(tree)
    assert len(tree.root.children) == 1
    assert "No processes" in tree.root.children[0].label

@patch("psutil.process_iter")
def test_populate_tree_filter(mock_iter, mock_process):
    p1 = Mock()
    p1.info = {"name": "python", "cmdline": ["py"]}
    p2 = Mock()
    p2.info = {"name": "java", "cmdline": ["java"]}
    mock_iter.return_value = [p1, p2]
    tree = Tree("test")
    populate_tree(tree, "py")
    assert len(tree.root.children) == 1
    assert "python" in tree.root.children[0].label

@patch("psutil.process_iter")
def test_children_map(mock_iter, mock_process):
    p1 = Mock()
    p1.pid = 1
    p1.ppid.return_value = 0
    p1.info = {"pid": 1, "ppid": 0}
    p2 = Mock()
    p2.pid = 42
    p2.ppid.return_value = 1
    p2.info = {"pid": 42, "ppid": 1}
    mock_iter.return_value = [p1, p2]
    tree = Tree("test")
    populate_tree(tree)
    # Root + 1 child
    assert len(tree.root.children) == 1

@patch("psutil.process_iter")
def test_roots_sort(mock_iter, mock_process):
    p1 = Mock()
    p1.create_time.return_value = 1000
    p1.info = {"pid": 10}
    p2 = Mock()
    p2.create_time.return_value = 500
    p2.info = {"pid": 20}
    mock_iter.return_value = [p1, p2]
    tree = Tree("test")
    populate_tree(tree)
    # Sorted by create_time asc
    assert int(tree.root.children[0].id) == 20