import pytest
from consistent_hash_simulator.ring import ConsistentHashRing

def test_single_node():
    ring = ConsistentHashRing(["only"])
    assert ring.get_node("anything") == "only"

def test_duplicate_nodes():
    ring = ConsistentHashRing(["x", "x"])
    assert len(ring.nodes) == 1