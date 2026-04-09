import pytest

from cache_eviction_simulator.policies import LRUCache, LFUCache, FIFOCache, RandomCache


@pytest.fixture(params=[LRUCache, LFUCache, FIFOCache, RandomCache])
def cache(request):
    return request.param(400)


def test_basic_miss(cache):
    cache.miss("a", 100)
    assert cache.has("a")
    assert cache.current_size == 100
    assert cache.evictions == 0


def test_lru_promotion():
    cache = LRUCache(300)
    cache.miss("a", 100)
    cache.miss("b", 100)
    cache.miss("c", 100)
    cache.hit("a")  # promote a
    cache.miss("d", 100)  # evict c (LRU)
    assert not cache.has("c")
    assert cache.has("a")


def test_fifo_order():
    cache = FIFOCache(300)
    cache.miss("a", 100)
    cache.miss("b", 100)
    cache.miss("c", 100)
    cache.miss("d", 100)  # evict a (FIFO)
    assert not cache.has("a")
    assert cache.has("b")


def test_lfu_frequency():
    cache = LFUCache(300)
    cache.miss("a", 100)
    cache.miss("b", 100)
    cache.hit("a")  # freq a=2, b=1
    cache.miss("c", 100)  # evict b (LFU)
    assert not cache.has("b")
    assert cache.has("a")


def test_random_varies():
    cache = RandomCache(200)
    cache.miss("a", 100)
    cache.miss("b", 100)
    victims = [cache._choose_victim() for _ in range(10)]  # private but test
    assert len(set(victims)) == 2  # a or b


def test_overflow_bytes(cache):
    cache.miss("large", 500)
    cache.miss("small", 100)  # evict large
    assert not cache.has("large")
    assert cache.has("small")