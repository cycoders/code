import pytest
from dep_tree_viz.tree_builder import DepNode, build_forest
from dep_tree_viz.renderer import render


def test_render_ascii():
    graph = {"root@1": ["child@2"]}
    forest = build_forest(["root@1"], graph)
    result = render(forest, "ascii")
    assert "root@1" in result
    assert "child@2" in result


def test_render_mermaid():
    graph = {"root@1": ["child@2"]}
    forest = build_forest(["root@1"], graph)
    result = render(forest, "mermaid")
    assert "flowchart TD" in result
    assert "root" in result
    assert "-->" in result


def test_render_png_bytes():
    graph = {"root@1": ["child@2"]}
    forest = build_forest(["root@1"], graph)
    result = render(forest, "png")
    assert isinstance(result, bytes)
    assert len(result) > 1000  # Minimal PNG


def test_invalid_format():
    graph = {"root@1": []}
    forest = build_forest(["root@1"], graph)
    with pytest.raises(ValueError, match="Unsupported"):
        render(forest, "foo")