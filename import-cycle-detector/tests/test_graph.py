import networkx as nx
import pytest
from pathlib import Path

from import_cycle_detector.graph import discover_modules, build_graph, get_file_path


class TestGraph:
    @pytest.mark.parametrize(
        "files,expected",
        [
            ({"a.py": ""}, {"a"}),
            ({"pkg/__init__.py": ""}, {"pkg"}),
            ({"pkg/b.py": ""}, {"pkg.b"}),
        ],
    )
    def test_discover_modules(self, tmp_path, files, expected):
        for rel, content in files.items():
            path = tmp_path / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        modules = discover_modules(tmp_path, [])
        assert modules == expected

    def test_get_file_path(self, tmp_path):
        (tmp_path / "pkg").mkdir()
        (tmp_path / "pkg" / "__init__.py").touch()
        assert get_file_path(tmp_path, "pkg") == tmp_path / "pkg" / "__init__.py"
        (tmp_path / "mod.py").touch()
        assert get_file_path(tmp_path, "mod") == tmp_path / "mod.py"

    def test_build_simple_cycle(self, tmp_path):
        tmp_path.joinpath("a.py").write_text("from b import x")
        tmp_path.joinpath("b.py").write_text("from a import y")
        G = build_graph(tmp_path, [])
        assert set(G.nodes) == {"a", "b"}
        assert G.has_edge("a", "b")
        assert G.has_edge("b", "a")

    def test_relative_cycle(self, tmp_path):
        pkg = tmp_path / "pkg"
        pkg.mkdir()
        pkg.joinpath("__init__.py").touch()
        pkg.joinpath("a.py").write_text("from .b import x")
        pkg.joinpath("b.py").write_text("from .a import y")
        G = build_graph(tmp_path, [])
        assert set(G.nodes) >= {"pkg.a", "pkg.b"}
        assert G.has_edge("pkg.a", "pkg.b")
        assert G.has_edge("pkg.b", "pkg.a")

    def test_exclude(self, tmp_path):
        tmp_path.joinpath("tests" / "a.py").write_text("")
        modules = discover_modules(tmp_path, ["tests"])
        assert "tests.a" not in modules