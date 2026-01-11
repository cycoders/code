from dep_tree_viz.tree_builder import DepNode, build_forest
import pytest


def test_build_simple():
    graph = {"root@1": ["child@2"], "child@2": []}
    forest = build_forest(["root@1"], graph)
    assert len(forest) == 1
    assert forest[0].namever == "root@1"
    assert len(forest[0].children) == 1
    assert forest[0].children[0].namever == "child@2"


def test_max_depth():
    graph = {"root@1": ["mid@2"], "mid@2": ["leaf@3"]}
    forest = build_forest(["root@1"], graph, max_depth=1)
    assert len(forest[0].children) == 1
    assert len(forest[0].children[0].children) == 0  # Pruned


def test_shared_memo():
    graph = {"root@1": ["shared@3", "shared@3"], "shared@3": ["leaf@4"]}
    forest = build_forest(["root@1"], graph)
    assert len(forest[0].children) == 2
    assert forest[0].children[0] is forest[0].children[1]  # Same object (memo)


def test_empty_roots():
    forest = build_forest([], {})
    assert len(forest) == 0