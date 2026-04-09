import pytest

from cache_eviction_simulator.simulator import CacheSimulator
from cache_eviction_simulator.policies import LRUCache, LFUCache


accesses = [("a", 100), ("b", 200), ("a", 100), ("c", 150), ("b", 200)]


def test_lru_sim():
    sim = CacheSimulator(LRUCache, 400)
    stats = sim.simulate(accesses)
    assert stats["hits"] == 2  # 2nd a, 2nd b
    assert stats["hit_rate"] == 2 / 5
    assert stats["evictions"] >= 1  # c evicts ?


def test_lfu_sim():
    sim = CacheSimulator(LFUCache, 400)
    stats = sim.simulate(accesses)
    assert stats["hits"] == 2
    assert "final_items" in stats


def test_byte_hit_rate():
    sim = CacheSimulator(LRUCache, 1000)
    byte_accesses = [("a", 100), ("a", 100)]
    stats = sim.simulate(byte_accesses)
    assert stats["byte_hit_rate"] == 100 / 200  # 2nd hit 100 bytes


def test_empty_trace():
    sim = CacheSimulator(LRUCache, 100)
    stats = sim.simulate([])
    assert stats["hit_rate"] == 0
    assert stats["accesses"] == 0


def test_max_size():
    sim = CacheSimulator(LRUCache, 300)
    sim.simulate([("a", 100), ("b", 200)])
    assert sim.max_size == 300