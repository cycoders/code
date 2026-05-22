import pytest
from consistent_hash_simulator.ring import ConsistentHashRing

def test_basic_placement():
    ring = ConsistentHashRing(["a", "b"])
    assert ring.get_node("test") in ["a", "b"]

def test_add_remove():
    ring = ConsistentHashRing(["a"])
    ring.add_node("b")
    ring.remove_node("a")
    assert ring.get_node("x") == "b"

def test_empty_ring():
    ring = ConsistentHashRing([])
    with pytest.raises(ValueError):
        ring.get_node("x")