from py_dep_graph.graph import DepGraph


class TestDepGraph:
    def test_add_edge(self):
        g = DepGraph()
        g.add_edge("a", "b")
        assert g.num_nodes == 2
        assert g.num_edges == 1
        assert "b" in g.adj["a"]

    def test_no_cycles(self):
        g = DepGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        assert g.cycles() == []

    def test_cycles(self):
        g = DepGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "a")
        cycles = g.cycles()
        assert len(cycles) == 1
        assert set(cycles[0]) == {"a", "b"}

    def test_complex_cycle(self):
        g = DepGraph()
        g.add_edge("a", "b")
        g.add_edge("b", "c")
        g.add_edge("c", "a")
        cycles = g.cycles()
        assert len(cycles) >= 1
        assert any(set(cyc) == {"a", "b", "c"} for cyc in cycles)
