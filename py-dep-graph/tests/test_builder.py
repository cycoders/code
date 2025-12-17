import pytest
from pathlib import Path
from py_dep_graph.builder import build_graph, compute_module_name


class TestBuilder:
    def test_compute_module_name(self, simple_proj: Path):
        assert compute_module_name(simple_proj, simple_proj / "main.py") == "main"
        assert compute_module_name(simple_proj, simple_proj / "utils.py") == "utils"

    def test_build_simple(self, simple_proj: Path):
        graph = build_graph(simple_proj)
        assert graph.num_nodes == 2
        assert graph.num_edges == 1
        assert "main" in graph.adj
        assert "utils" in graph.adj["main"]

    def test_build_cycle(self, cycle_proj: Path):
        graph = build_graph(cycle_proj)
        assert graph.num_nodes == 2
        assert graph.num_edges == 2  # mutual

    def test_no_py_files(self):
        with pytest.raises(ValueError, match="No Python files"):
            build_graph(Path("nonexistent"))
