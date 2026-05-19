from idempotency_guard.backends.memory import MemoryBackend

def test_memory_set_get_delete():
    b = MemoryBackend()
    b.set("k", {"v": 1}, 60)
    assert b.get("k")["v"] == 1
    b.delete("k")
    assert b.get("k") is None