import networkx as nx
from import_cycle_detector.cycles import find_cycles


def test_find_cycles_acyclic():
    G = nx.DiGraph([("a", "b"), ("b", "c")])
    cycles = find_cycles(G)
    assert cycles == []


def test_find_cycles_cyclic():
    G = nx.DiGraph([("a", "b"), ("b", "a"), ("c", "d")])
    cycles = find_cycles(G)
    assert len(cycles) == 1
    assert set(cycles[0]) == {"a", "b"}


def test_multi_cycle():
    G = nx.DiGraph([("a", "b"), ("b", "c"), ("c", "a"), ("a", "d")])
    cycles = find_cycles(G)
    assert len(cycles) >= 1  # At least triangle